# 在 plan/planner.py 中创建一个不使用 Agno 的简化版本
import openai
import os
from typing import List, Optional, Dict, Any
import json

class SimplePlanner:
    """
    完全独立于 Agno 的 Planner，直接使用 OpenAI API
    """
    
    def __init__(self, agent_connections: RemoteConnections):
        self.agent_connections = agent_connections
        self.client = openai.OpenAI(
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = "gpt-4"  # 使用您可用的模型

    async def create_plan(
        self,
        user_input: UserInput,
        user_input_callback: Callable,
        thread_id: str,
    ) -> ExecutionPlan:
        """
        完全独立创建执行计划
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
            user_input, conversation_id
        )
        plan.tasks = tasks
        plan.guidance_message = guidance_message

        return plan

    async def _direct_planning(
        self,
        user_input: UserInput,
        conversation_id: str,
    ) -> tuple[List[Task], Optional[str]]:
        """
        直接调用 OpenAI API，完全绕过 Agno
        """
        try:
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

            # 直接调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            # 解析响应
            content = response.choices[0].message.content
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
                task = Task(
                    conversation_id=user_input.meta.conversation_id,
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

        except Exception as e:
            error_msg = f"Direct planning failed: {str(e)}"
            logger.error(error_msg)
            return [], error_msg