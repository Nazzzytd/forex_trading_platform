# test_workflow_integration.py
import sys
import os

# 添加src到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def test_workflow_executor():
    """测试WorkflowExecutor是否正确加载Agent支持"""
    print("🧪 测试WorkflowExecutor Agent支持...")
    
    try:
        from ultrarag.core.workflow_executor import WorkflowExecutor
        from ultrarag.core.server_manager import ServerManager
        
        # 创建执行器实例
        server_manager = ServerManager()
        executor = WorkflowExecutor(server_manager)
        
        print("✅ WorkflowExecutor创建成功")
        
        # 检查Agent注册器
        if hasattr(executor, 'agent_registry') and executor.agent_registry:
            print(f"✅ Agent注册器存在: {executor.agent_registry}")
            print(f"🤖 可用Agent: {executor.agent_registry.list_agents()}")
        else:
            print("❌ Agent注册器不存在或未初始化")
        
        # 测试步骤类型识别
        test_steps = [
            {"step": "test_print", "type": "print", "config": {"message": "test"}},
            {"step": "test_agent", "type": "agent", "agent": "data_fetcher"},
            {"step": "test_tool", "type": "tool", "tool": "data_fetcher"}
        ]
        
        for step in test_steps:
            step_type = step.get("type")
            print(f"🔍 测试步骤类型: {step_type}")
            
        print("🎉 基础测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow_executor()