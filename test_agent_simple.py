import sys
import os
import asyncio

print("🧪 开始测试 DataFetcher Agent...")

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

print(f"📁 工作目录: {current_dir}")
print(f"📁 添加路径: {src_path}")

try:
    # 直接导入Agent类
    from agents.data_fetcher_agent.agent import DataFetcherAgent
    print("✅ DataFetcherAgent 导入成功!")
    
    async def test_agent():
        agent = DataFetcherAgent()
        print(f"✅ Agent实例创建成功: {agent.name}")
        
        # 测试基本信息
        info = agent.get_info()
        print(f"🔹 Agent信息: {info}")
        
        print("🎉 基础测试通过!")
    
    asyncio.run(test_agent())
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n🔍 调试信息:")
    
    # 检查agents目录结构
    agents_dir = os.path.join(src_path, 'agents')
    if os.path.exists(agents_dir):
        print("Agents目录结构:")
        for root, dirs, files in os.walk(agents_dir):
            level = root.replace(agents_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.py'):
                    print(f'{subindent}{file}')
    else:
        print("❌ agents目录不存在!")
        
except Exception as e:
    print(f"❌ 其他错误: {e}")
    import traceback
    traceback.print_exc()
