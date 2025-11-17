# test_agent_full.py
import sys
import os
import asyncio

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

async def test_full_functionality():
    """测试DataFetcher Agent的完整功能"""
    print("🧪 测试 DataFetcher Agent 完整功能...")
    
    try:
        from agents.data_fetcher_agent.agent import DataFetcherAgent
        
        agent = DataFetcherAgent()
        print(f"✅ Agent: {agent.name}")
        
        # 1. 测试健康检查
        print("\n1. 🩺 健康检查...")
        health = await agent.health_check()
        print(f"   状态: {health.get('status')}")
        print(f"   API连接: {health.get('api_connected')}")
        if health.get('error'):
            print(f"   错误: {health.get('error')}")
        
        # 2. 测试实时数据获取
        print("\n2. 📈 测试实时数据获取...")
        realtime_result = await agent.execute({
            "currency_pair": "EUR/USD",
            "data_type": "realtime"
        })
        
        print(f"   成功: {realtime_result.get('success')}")
        if realtime_result.get('success'):
            data = realtime_result.get('data', {})
            print(f"   汇率: {data.get('exchange_rate', 'N/A')}")
            print(f"   涨跌幅: {data.get('percent_change', 'N/A')}%")
            print(f"   时间: {data.get('timestamp', 'N/A')}")
        else:
            print(f"   错误: {realtime_result.get('error')}")
        
        # 3. 测试历史数据获取
        print("\n3. 📊 测试历史数据获取...")
        historical_result = await agent.execute({
            "currency_pair": "EUR/USD", 
            "data_type": "historical",
            "interval": "1h",
            "output_size": 10
        })
        
        print(f"   成功: {historical_result.get('success')}")
        if historical_result.get('success'):
            data = historical_result.get('data', [])
            summary = historical_result.get('summary', {})
            print(f"   数据条数: {len(data)}")
            print(f"   日期范围: {summary.get('date_range', {})}")
            if data:
                print(f"   最新数据: {data[0]}")
        else:
            print(f"   错误: {historical_result.get('error')}")
        
        # 4. 测试使用统计
        print("\n4. 📊 测试使用统计...")
        stats = await agent.get_usage_stats()
        print(f"   每日请求数: {stats.get('daily_requests_used', 0)}")
        print(f"   剩余请求数: {stats.get('daily_requests_remaining', 0)}")
        
        # 5. 测试能力描述
        print("\n5. 🔧 测试能力描述...")
        capabilities = await agent.get_capabilities()
        print(f"   支持的数据类型: {capabilities.get('supported_data_types')}")
        print(f"   支持的时间框架: {capabilities.get('supported_intervals')}")
        
        print("\n🎉 完整功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_functionality())