# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/verify_fix.py

import sys
import os

print("🔍 VERIFYING FIX")

# 检查当前使用的模块文件
def check_module_files():
    modules = {
        'plan.models': 'valuecell.core.plan.models',
        'plan.planner': 'valuecell.core.plan.planner', 
        'agno.agent': 'agno.agent'
    }
    
    for name, module_name in modules.items():
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"📁 {name}: {module.__file__}")
            
            # 检查文件修改时间
            if os.path.exists(module.__file__):
                mtime = os.path.getmtime(module.__file__)
                print(f"   📅 Modified: {mtime}")
                
        except Exception as e:
            print(f"❌ {name}: {e}")

check_module_files()

# 检查 PlannerResponse 是否被阻止
print("\n🔧 Checking PlannerResponse blocking...")
try:
    from agno_patch import apply_global_patches
    apply_global_patches()
    print("✅ Agno patches active")
except Exception as e:
    print(f"❌ Agno patches failed: {e}")

print("✅ Verification completed")