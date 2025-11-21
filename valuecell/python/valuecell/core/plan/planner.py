"""Planner: create execution plans from user input.

This module implements the ExecutionPlanner which uses an LLM-based
planning agent to convert a user request into a structured
`ExecutionPlan` consisting of `Task` objects. The planner supports
Human-in-the-Loop flows by emitting `UserInputRequest` objects (backed by
an asyncio.Event) when the planner requires clarification.

The planner is intentionally thin: it delegates reasoning to an AI agent
and performs JSON parsing/validation of the planner's output.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Callable, List, Optional, Dict, Any

import openai
from a2a.types import AgentCard

import valuecell.utils.model as model_utils_mod
from valuecell.core.agent.connect import RemoteConnections
from valuecell.core.task.models import Task, TaskStatus
from valuecell.core.types import UserInput
from valuecell.utils import generate_uuid
from valuecell.utils.env import agent_debug_mode_enabled
from valuecell.utils.uuid import generate_conversation_id

from .models import ExecutionPlan, PlannerInput
from .prompts import (
    PLANNER_EXPECTED_OUTPUT,
    PLANNER_INSTRUCTION,
)

logger = logging.getLogger(__name__)


class UserInputRequest:
    """
    Represents a request for user input during plan creation or execution.

    This class uses asyncio.Event to enable non-blocking waiting for user responses
    in the Human-in-the-Loop workflow.
    """

    def __init__(self, prompt: str):
        """Create a new request object for planner-driven user input.

        Args:
            prompt: Human-readable prompt describing the information needed.
        """
        self.prompt = prompt
        self.response: Optional[str] = None
        self.event = asyncio.Event()

    async def wait_for_response(self) -> str:
        """Block until a response is provided and return it.

        This is an awaitable helper designed to be used by planner code that
        wants to pause execution until the external caller supplies the
        requested value via `provide_response`.
        """
        await self.event.wait()
        return self.response

    def provide_response(self, response: str):
        """Supply the user's response and wake any waiter.

        Args:
            response: The text provided by the user to satisfy the prompt.
        """
        self.response = response
        self.event.set()


class SimplePlanner:
    """
    完全独立于 Agno 的 Planner，直接使用 OpenAI API
    """
    
    def __init__(self, agent_connections: RemoteConnections):
        self.agent_connections = agent_connections
        
        # 使用项目现有的模型配置系统
        model = model_utils_mod.get_model_for_agent("super_agent")
        
        # 从模型配置中获取连接信息
        self.api_base = getattr(model, 'base_url', 'https://zjuapi.com/v1')
        self.api_key = getattr(model, 'api_key', None) or os.getenv('OPENAI_COMPATIBLE_API_KEY')
        self.model_name = model.id
        
        if not self.api_key:
            logger.error("API key is not configured!")
            raise ValueError("API key is required")
            
        logger.info(f"Using model: {self.model_name}, base_url: {self.api_base}")
        
        # 创建 OpenAI 客户端
        self.client = openai.OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )

    async def create_plan(
        self,
        user_input: UserInput,
        user_input_callback: Callable,
        thread_id: str,
    ) -> ExecutionPlan:
        """
        创建执行计划 - 这是被调用的主要方法
        """
        conversation_id = user_input.meta.conversation_id
        plan = ExecutionPlan(
            plan_id=generate_uuid("plan"),
            conversation_id=conversation_id,
            user_id=user_input.meta.user_id,
            orig_query=user_input.query,
            created_at=datetime.now().isoformat(),
        )

        # 使用直接 API 调用
        tasks, guidance_message = await self._direct_planning(
            user_input, conversation_id, thread_id
        )
        plan.tasks = tasks
        plan.guidance_message = guidance_message

        return plan

    async def _direct_planning(
        self,
        user_input: UserInput,
        conversation_id: str,
        thread_id: str,
    ) -> tuple[List[Task], Optional[str]]:
        """
        直接调用 OpenAI API，完全绕过 Agno
        """
        try:
            logger.info(f"Starting direct planning with model: {self.model_name}")
            
            # 构建提示
            system_prompt = PLANNER_INSTRUCTION + """

你必须输出严格的 JSON 格式，包含以下字段：
- tasks: 任务数组，每个任务包含 title, query, agent_name
- adequate: true/false  
- reason: 决策原因
- guidance_message: 可选的用户指导信息

只输出 JSON，不要其他内容。
"""

            user_prompt = f"""
目标代理: {user_input.target_agent_name}
用户查询: {user_input.query}
"""

            logger.info("Sending request to OpenAI API...")

            # 直接调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            logger.info("Successfully received response from API")
            
            # 解析响应
            content = response.choices[0].message.content
            logger.info(f"Raw planner response: {content}")
            plan_data = json.loads(content)

            # 验证必需字段
            if not all(key in plan_data for key in ['tasks', 'adequate', 'reason']):
                raise ValueError("Missing required fields")

            tasks_data = plan_data.get('tasks', [])
            adequate = bool(plan_data.get('adequate', False))
            reason = str(plan_data.get('reason', ''))
            guidance_message = plan_data.get('guidance_message')

            logger.info(f"Direct planning result: adequate={adequate}, tasks={len(tasks_data)}")

            # 如果不充分或没有任务
            if not adequate or not tasks_data:
                return [], guidance_message or reason

            # 创建任务
            tasks = []
            for task_info in tasks_data:
                # 重用父线程 ID
                task_conversation_id = user_input.meta.conversation_id
                if not user_input.target_agent_name:  # 从 Super Agent 转交
                    task_conversation_id = generate_conversation_id()

                task = Task(
                    conversation_id=task_conversation_id,
                    thread_id=thread_id,
                    user_id=user_input.meta.user_id,
                    agent_name=task_info.get('agent_name', 'unknown'),
                    status=TaskStatus.PENDING,
                    title=task_info.get('title', ''),
                    query=task_info.get('query', ''),
                    pattern="once",  # 简化
                    schedule_config=None,
                    handoff_from_super_agent=(not user_input.target_agent_name),
                )
                tasks.append(task)

            return tasks, None

        except openai.AuthenticationError as e:
            error_msg = f"API authentication failed: {str(e)}. Please check your API key and base URL."
            logger.error(error_msg)
            return [], error_msg
        except openai.APIConnectionError as e:
            error_msg = f"API connection failed: {str(e)}. Please check your network connection and base URL."
            logger.error(error_msg)
            return [], error_msg
        except openai.APIError as e:
            error_msg = f"OpenAI API error: {str(e)}"
            logger.error(error_msg)
            return [], error_msg
        except Exception as e:
            error_msg = f"Direct planning failed: {str(e)}"
            logger.error(error_msg)
            return [], error_msg

class ExecutionPlanner:
    """
    Creates execution plans by analyzing user input and determining appropriate agent tasks.
    """

    # 在 ./python/valuecell/core/plan/planner.py 的 ExecutionPlanner.__init__ 方法中添加调试代码

class ExecutionPlanner:
    def __init__(
        self,
        agent_connections: RemoteConnections,
    ):
        # 添加调试信息
        import traceback
        print(f"🚨🚨🚨 ExecutionPlanner CREATED at {id(self)} 🚨🚨🚨")
        print("Creation stack trace:")
        for line in traceback.format_stack()[-6:-1]:
            if 'valuecell' in line and 'test' not in line:
                print(f"  {line.strip()}")
        print("=" * 80)
        
        self.agent_connections = agent_connections
        # 使用我们独立的 SimplePlanner，完全绕过 Agno
        self.simple_planner = SimplePlanner(agent_connections)
        
    async def create_plan(
        self,
        user_input: UserInput,
        user_input_callback: Callable,
        thread_id: str,
    ) -> ExecutionPlan:
        """
        Create an execution plan from user input.
        """
        # 直接委托给 SimplePlanner
        return await self.simple_planner.create_plan(user_input, user_input_callback, thread_id)