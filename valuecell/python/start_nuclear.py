#!/usr/bin/env python3
"""
核武器启动脚本 - 强制应用所有补丁
"""
import sys
import os

# 强制路径
sys.path.insert(0, '/Users/fr./answer/forex_trading_platform/valuecell/python')

print("💣 STARTING NUCLEAR LAUNCHER")

# 1. 首先应用补丁
try:
    from agno_patch import apply_global_patches
    apply_global_patches()
    print("✅ Nuclear patches applied")
except Exception as e:
    print(f"❌ Failed to apply patches: {e}")
    sys.exit(1)

# 2. 导入并启动原有应用
try:
    from scripts.launch import main
    print("✅ Starting main application...")
    main()
except Exception as e:
    print(f"❌ Failed to start application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
