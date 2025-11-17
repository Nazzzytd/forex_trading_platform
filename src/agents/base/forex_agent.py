# src/agents/base/forex_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class ForexAgent(ABC):
    """外汇交易Agent基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "name": self.name,
            "description": self.description,
            "type": "forex_agent"
        }