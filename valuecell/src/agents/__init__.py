print("🔧 初始化agents模块...")

try:
    from .registry.simple_registry import registry
    
    def setup_agents():
        """设置并注册所有Agent"""
        try:
            from .data_fetcher_agent.agent import DataFetcherAgent
            registry.register(DataFetcherAgent())
            print(f"✅ 注册DataFetcherAgent成功")
        except Exception as e:
            print(f"❌ 注册DataFetcherAgent失败: {e}")
        
        agent_count = len(registry.list_agents())
        print(f"🎯 已注册 {agent_count} 个Agent: {registry.list_agents()}")
        return registry
    
    # 自动设置
    agents_registry = setup_agents()
    print("🔧 agents模块初始化完成")
    
except Exception as e:
    print(f"❌ agents模块初始化失败: {e}")
    agents_registry = None
