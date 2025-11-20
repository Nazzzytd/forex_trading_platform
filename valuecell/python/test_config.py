# test_config.py
import os
import sys
sys.path.append('/Users/fr./answer/forex_trading_platform/valuecell/python')

from valuecell.config.manager import get_config_manager

def test_config():
    print("Testing configuration loading...")
    
    # 设置环境变量
    os.environ['OPENAI_COMPATIBLE_API_KEY'] = 'your_test_key_here'
    
    try:
        manager = get_config_manager()
        
        # 测试主提供商
        primary = manager.primary_provider
        print(f"✅ Primary provider: {primary}")
        
        # 测试启用的提供商
        enabled = manager.get_enabled_providers()
        print(f"✅ Enabled providers: {enabled}")
        
        # 测试提供商配置
        provider_config = manager.get_provider_config(primary)
        if provider_config:
            print(f"✅ Provider config loaded: {provider_config.name}")
            print(f"   API Key: {'***' + provider_config.api_key[-4:] if provider_config.api_key else 'None'}")
            print(f"   Base URL: {provider_config.base_url}")
            print(f"   Default Model: {provider_config.default_model}")
        else:
            print("❌ Failed to load provider config")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_config()