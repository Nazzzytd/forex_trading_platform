# test_yaml_loading.py
import os
import yaml
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def test_yaml_loading():
    try:
        # 读取 news_agent.yaml 配置
        with open("configs/agents/news_agent.yaml", 'r') as file:
            config = yaml.safe_load(file)
        
        print("📄 YAML 配置内容:")
        print(yaml.dump(config, default_flow_style=False))
        
        # 从配置中提取模型信息
        model_config = config["models"]["primary"]
        
        # 手动创建模型实例
        model = OpenAIChat(
            id=model_config["model_id"],
            base_url="https://zjuapi.com/v1",
            api_key=os.getenv("OPENAI_COMPATIBLE_API_KEY"),
            temperature=model_config["parameters"]["temperature"],
            max_tokens=model_config["parameters"]["max_tokens"]
        )
        
        # 创建 agent
        agent = Agent(
            name=config["name"],
            model=model,
            description=config["description"]
        )
        
        print("🚀 测试 YAML 配置的 agent...")
        # 注意：不需要 await！
        response = agent.run("What's the latest forex news? Reply briefly.")
        print(f"✅ YAML 配置测试成功!")
        print(f"响应: {response.content}")
        
    except Exception as e:
        print(f"❌ YAML 配置测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_yaml_loading()