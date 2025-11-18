# test_config.py
from valuecell.config.manager import get_config_manager

def test_config():
    config_manager = get_config_manager()
    
    # 检查 News Agent 配置
    news_agent_config = config_manager.get_agent_config("news_agent")
    print("News Agent enabled:", news_agent_config.enabled)
    
    # 检查 OpenAI 提供商
    openai_config = config_manager.get_provider_config("openai")
    print("OpenAI enabled:", openai_config.enabled)
    print("OpenAI API key set:", bool(openai_config.api_key))