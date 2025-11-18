# test_provider_models.py
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def test_provider_models():
    # 测试几个关键模型
    test_models = [
        "gpt-3.5-turbo",      # 最兼容
        "gpt-4o-mini",        # 性价比高
        "gpt-4.1-mini",       # 较新模型
        "gpt-5-mini"          # 最新系列
    ]
    
    for model_id in test_models:
        try:
            print(f"\n🧪 测试模型: {model_id}")
            
            # 正确的方式：直接创建模型实例
            model = OpenAIChat(
                id=model_id,
                base_url="https://zjuapi.com/v1",
                api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY"),
                temperature=0.1,
                max_tokens=100
            )
            
            agent = Agent(
                name=f"Test Agent - {model_id}",
                model=model
            )
            
            # 注意：不需要 await！
            response = agent.run("Say 'hello' in one word")
            print(f"✅ {model_id} - 测试成功: {response.content}")
            
        except Exception as e:
            print(f"❌ {model_id} - 测试失败: {str(e)[:100]}")

if __name__ == "__main__":
    test_provider_models()