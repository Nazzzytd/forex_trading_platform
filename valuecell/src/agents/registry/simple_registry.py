# src/agents/registry/simple_registry.py
from typing import Dict, Optional, List, Any
from ..base.forex_agent import ForexAgent

class AgentRegistry:
    """简单的Agent注册中心"""
    
    def __init__(self):
        self._agents: Dict[str, ForexAgent] = {}
    
    def register(self, agent: ForexAgent):
        """注册Agent"""
        self._agents[agent.name] = agent
        print(f"✅ 注册Agent: {agent.name} - {agent.description}")
    
    def get_agent(self, name: str) -> Optional[ForexAgent]:
        """获取Agent"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """列出所有Agent名称"""
        return list(self._agents.keys())
    
    def get_agents_info(self) -> Dict[str, Any]:
        """获取所有Agent的详细信息"""
        return {
            agent_name: agent.get_info()
            for agent_name, agent in self._agents.items()
        }

# 全局注册器实例
registry = AgentRegistry()