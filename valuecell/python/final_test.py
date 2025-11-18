# final_test.py
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def test_with_schema_fix():
    """测试并应用 schema 修复"""
    try:
        # 首先应用 schema 修复
        from schema_fix import patch_superagent_outcome
        patch_superagent_outcome()
        
        # 测试模型
        model = OpenAIChat(
            id="gpt-3.5-turbo",
            base_url="https://zjuapi.com/v1",
            api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY"),
            temperature=0.2,
            max_tokens=100
        )
        
        agent = Agent(
            name="Final Test Agent",
            model=model
        )
        
        response = agent.run("Say 'success' if everything is working")
        print(f"✅ 最终测试成功: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 最终测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_schema_fix()
    if success:
        print("\n🎉 所有测试通过！现在可以启动你的应用了。")
    else:
        print("\n💥 测试失败，需要进一步调试。")