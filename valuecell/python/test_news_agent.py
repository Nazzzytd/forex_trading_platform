#!/usr/bin/env python3
"""
Test script for News Agent configuration and functionality.
"""

import os
import sys
sys.path.append('/Users/fr./answer/forex_trading_platform/valuecell/python')

from valuecell.config.manager import get_config_manager
from valuecell.adapters.assets.manager import get_adapter_manager

def test_news_agent_config():
    """Test News Agent configuration."""
    print("🔍 Testing News Agent Configuration...")
    
    manager = get_config_manager()
    
    # Test agent configuration
    agent_config = manager.get_agent_config("NewsAgent")
    if agent_config:
        print(f"✅ News Agent enabled: {agent_config.enabled}")
        print(f"✅ Primary model: {agent_config.primary_model.model_id}")
        print(f"✅ Provider: {agent_config.primary_model.provider}")
        print(f"✅ Capabilities: {list(agent_config.capabilities.keys())}")
    else:
        print("❌ News Agent configuration not found")
        return False
    
    return True

def test_asset_adapters():
    """Test asset adapters."""
    print("\n🔍 Testing Asset Adapters...")
    
    adapter_manager = get_adapter_manager()
    
    # Test available adapters
    adapters = adapter_manager.get_available_adapters()
    print(f"✅ Available adapters: {[a.value for a in adapters]}")
    
    # Test forex pair lookup
    test_pairs = ["FX:EURUSD", "FX:GBPUSD", "FX:USDJPY"]
    
    for pair in test_pairs:
        adapter = adapter_manager.get_adapter_for_ticker(pair)
        if adapter:
            print(f"✅ Adapter found for {pair}: {adapter.source.value}")
            
            # Test price lookup
            price = adapter_manager.get_real_time_price(pair)
            if price:
                print(f"✅ Price for {pair}: {price.price}")
            else:
                print(f"⚠️  No price data for {pair}")
        else:
            print(f"❌ No adapter found for {pair}")
    
    return len(adapters) > 0

def test_api_keys():
    """Test API key configuration."""
    print("\n🔍 Testing API Keys...")
    
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

if __name__ == "__main__":
    print("🚀 Starting News Agent Test Suite...\n")
    
    tests = [
        test_api_keys,
        test_asset_adapters, 
        test_news_agent_config
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
        print("🎉 All tests passed! News Agent should be ready to use.")
    else:
        print("❌ Some tests failed. Please check the configuration.")