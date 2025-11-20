# comprehensive_fix.py
import os
import sys

def apply_comprehensive_fixes():
    """应用综合修复方案"""
    
    print("🛠️ 应用综合修复...")
    
    # 1. 设置环境变量
    env_vars = {
        'AGNO_DISABLE_STRICT_SCHEMA': 'true',
        'AGNO_USE_COMPATIBLE_MODE': 'true', 
        'OPENAI_COMPATIBILITY_MODE': 'true',
        'AGNO_USE_LEGACY_RESPONSE_FORMAT': 'true'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ 设置环境变量: {key}={value}")
    
    # 2. 尝试导入并修补 agno
    try:
        import agno
        agno._compatibility_mode = True
        print("✅ Agno 兼容模式启用")
    except Exception as e:
        print(f"⚠️ Agno 兼容模式设置失败: {e}")
    
    # 3. 尝试修补 openai
    try:
        import openai
        # 设置更宽松的配置
        openai.api_version = "2023-05-15"  # 使用较旧的 API 版本
        print("✅ OpenAI 配置调整")
    except Exception as e:
        print(f"⚠️ OpenAI 配置调整失败: {e}")
    
    print("🎉 综合修复应用完成")
    return True

if __name__ == "__main__":
    apply_comprehensive_fixes()