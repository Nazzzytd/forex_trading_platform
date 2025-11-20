#!/usr/bin/env python3
"""
Fixed test script with proper environment loading.
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 从项目根目录的 .env 文件加载环境变量
env_file = project_root / ".env"
if env_file.exists():
    print(f"📁 Loading environment from: {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
else:
    print(f"❌ .env file not found at: {env_file}")

def test_api_keys():
    """Test API key configuration."""
    print("🔍 Testing API Keys...")
    
    required_keys = [
        "OPENAI_COMPATIBLE_API_KEY",
        "ALPHA_VANTAGE_API_KEY", 
        "TWELVE_DATA_API_KEY"
    ]
    
    all_valid = True
    for key in required_keys:
        value = os.getenv(key)
        if value:
            print(f"✅ {key}: ***{value[-4:]}")
        else:
            print(f"❌ {key}: Not set")
            all_valid = False
    
    return all_valid

def test_config_manager():
    """Test configuration manager."""
    print("\n🔍 Testing Configuration Manager...")
    
    try:
        from valuecell.config.manager import get_config_manager
        
        manager = get_config_manager()
        print("✅ Configuration manager initialized")
        
        # Test primary provider
        primary = manager.primary_provider
        print(f"✅ Primary provider: {primary}")
        
        # Test enabled providers
        enabled = manager.get_enabled_providers()
        print(f"✅ Enabled providers: {enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")
        return False

def test_basic_imports():
    """Test basic imports without problematic types."""
    print("\n🔍 Testing Basic Imports...")
    
    try:
        # 测试基本导入
        from valuecell.adapters.assets.types import AssetType, Exchange, DataSource
        print("✅ Basic types imported successfully")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in types.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Fixed Test Suite...\n")
    
    tests = [
        test_api_keys,
        test_basic_imports,
        test_config_manager
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All basic tests passed!")
    else:
        print("❌ Some tests failed. Please check the configuration.")