# debug_workflow_executor.py
import sys
import os

# 添加src到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def debug_workflow_executor():
    """调试WorkflowExecutor的实际代码"""
    print("🔧 调试WorkflowExecutor...")
    
    try:
        # 导入并检查实际的WorkflowExecutor
        from ultrarag.core.workflow_executor import WorkflowExecutor
        
        # 检查类定义
        print(f"✅ WorkflowExecutor类: {WorkflowExecutor}")
        
        # 检查_execute_step方法
        if hasattr(WorkflowExecutor, '_execute_step'):
            print("✅ _execute_step方法存在")
            
            # 获取方法的源代码（前几行）
            import inspect
            source = inspect.getsource(WorkflowExecutor._execute_step)
            lines = source.split('\n')
            print("📝 _execute_step方法内容:")
            for i, line in enumerate(lines[:20]):  # 只显示前20行
                print(f"  {i+1}: {line}")
                
            # 检查是否包含agent类型支持
            if 'type: agent' in source or "step_type == \"agent\"" in source:
                print("🎯 检测到Agent步骤类型支持!")
            else:
                print("❌ 未检测到Agent步骤类型支持!")
        else:
            print("❌ _execute_step方法不存在")
            
        # 检查AgentManager支持
        if hasattr(WorkflowExecutor, 'agent_manager'):
            print("✅ agent_manager属性存在")
        else:
            print("❌ agent_manager属性不存在")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflow_executor()