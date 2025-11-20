from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from valuecell.core.task.models import ScheduleConfig, Task

# 使用 Literal 完全避免枚举问题
TaskPatternType = Literal["once", "recurring"]


class ExecutionPlan(BaseModel):
    """Execution plan containing multiple tasks for fulfilling a user request."""
    plan_id: str = Field(..., description="Unique plan identifier")
    conversation_id: Optional[str] = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    orig_query: str = Field(..., description="Original user query")
    tasks: List[Task] = Field(default_factory=list, description="Tasks to execute")
    created_at: str = Field(..., description="Plan creation timestamp")
    guidance_message: Optional[str] = Field(None, description="Guidance message")


class _TaskBrief(BaseModel):
    """Simplified task representation for planning phase."""
    title: str = Field(..., description="Task title")
    query: str = Field(..., description="Task to be performed") 
    agent_name: str = Field(..., description="Agent name")
    pattern: TaskPatternType = Field(default="once", description="Execution pattern")
    schedule_config: Optional[ScheduleConfig] = Field(None, description="Schedule config")


class PlannerInput(BaseModel):
    """Schema for planner input."""
    target_agent_name: str = Field(..., description="Target agent name")
    query: str = Field(..., description="User query")


# 完全重命名 PlannerResponse 以避免任何缓存
class PlanResponseModel(BaseModel):
    """COMPLETELY NEW response model to avoid all caching issues"""
    tasks: List[_TaskBrief] = Field(..., description="List of tasks to be executed")
    adequate: bool = Field(..., description="Whether info is adequate for execution")
    reason: str = Field(..., description="Reason for the planning decision")
    guidance_message: Optional[str] = Field(None, description="User guidance message")

    class Config:
        extra = "forbid"


# 不创建任何别名！完全使用新名称