# src/ultrarag/core/agent_manager.py
class AgentManager:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._agents = {}
        self._initialized = False
    
    def _initialize_agents(self):
        if self._initialized:
            return
            
        try:
            from ...agents import agents_registry
            self._agents = {name: agents_registry.get_agent(name) 
                          for name in agents_registry.list_agents()}
            
            if self.verbose:
                print(f"🔧 Agent系统已加载: {list(self._agents.keys())}")
            
            self._initialized = True
        except ImportError as e:
            print(f"⚠️  Agent系统未初始化: {e}")
    
    def get_agent(self, agent_name: str):
        self._initialize_agents()
        return self._agents.get(agent_name)
    
    def list_agents(self):
        self._initialize_agents()
        return list(self._agents.keys())