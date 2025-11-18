# check_agno_api.py
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def check_agno_api():
    print("🔍 检查 Agno Agent 类的可用方法...")
    
    # 检查 Agent 类的方法
    methods = [method for method in dir(Agent) if not method.startswith('_')]
    print("Agent 类的方法:", methods)
    
    print("\n🔍 检查 Agent 的 __init__ 参数...")
    import inspect
    sig = inspect.signature(Agent.__init__)
    print("Agent.__init__ 参数:", list(sig.parameters.keys()))
    
    # 测试最简单的配置
    print("\n🧪 测试最简单配置...")
    try:
        model = OpenAIChat(
            id="gpt-3.5-turbo",
            base_url="https://zjuapi.com/v1",
            api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY")
        )
        
        agent = Agent(
            name="Simple Test",
            model=model
        )
        
        # 注意：不需要 await！
        response = agent.run("Hello")
        print(f"✅ 简单配置成功: {response.content}")
        
    except Exception as e:
        print(f"❌ 简单配置失败: {e}")

if __name__ == "__main__":
    check_agno_api()