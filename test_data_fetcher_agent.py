# test_data_fetcher_agent.py (项目根目录)
import asyncio
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

async def test_data_fetcher_agent():
    """测试DataFetcher Agent"""
    print("🧪 测试 DataFetcher Agent...")
    
    try:
        # 直接导入Agent类，避免复杂的路径问题
        from agents.data_fetcher_agent.agent import DataFetcherAgent
        
        # 创建Agent实例
        agent = DataFetcherAgent()
        print(f"✅ 成功创建Agent: {agent.name}")
        
        print("1. 测试实时数据获取...")
        result = await agent.execute({
            "currency_pair": "EUR/USD",
            "data_type": "realtime"
        })
        
        print("📊 实时数据结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  Agent: {result.get('agent')}")
        print(f"  货币对: {result.get('currency_pair')}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"  汇率: {data.get('exchange_rate', 'N/A')}")
            print(f"  涨跌幅: {data.get('percent_change', 'N/A')}%")
        else:
            print(f"  错误: {result.get('error')}")
        
        print("\n2. 测试健康检查...")
        health = await agent.health_check()
        print(f"  健康状态: {health.get('status')}")
        print(f"  API连接: {health.get('api_connected')}")
        
        print("\n3. 测试能力描述...")
        capabilities = await agent.get_capabilities()
        print(f"  支持的数据类型: {capabilities.get('supported_data_types')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_data_fetcher_agent())