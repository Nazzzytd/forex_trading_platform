# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/start_patched.py

#!/usr/bin/env python3
"""
修复版启动脚本
"""
import sys
import os

print("🚀 STARTING PATCHED APPLICATION")

# 强制我们的路径在最前面
sys.path.insert(0, '/Users/fr./answer/forex_trading_platform/valuecell/python')

# 1. 首先应用补丁
try:
    print("📝 Applying Agno patches...")
    from agno_patch import apply_global_patches
    apply_global_patches()
    print("✅ Agno patches applied successfully")
except Exception as e:
    print(f"❌ Failed to apply Agno patches: {e}")
    import traceback
    traceback.print_exc()

# 2. 启动原有应用
try:
    print("🎯 Starting main application...")
    from scripts.launch import main
    main()
except Exception as e:
    print(f"💥 Application failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)