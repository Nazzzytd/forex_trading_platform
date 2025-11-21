# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/force_reload.py

import sys
import importlib

def force_reload_modules():
    """强制重载所有可能相关的模块"""
    modules_to_reload = [
        'valuecell.core.plan.models',
        'valuecell.core.plan.planner', 
        'valuecell.core.plan.service',
        'agno.agent'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"🔄 Reloading: {module_name}")
            importlib.reload(sys.modules[module_name])
        else:
            print(f"📦 Importing: {module_name}")
            importlib.import_module(module_name)

force_reload_modules()
print("✅ Force reload completed")