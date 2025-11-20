# /Users/fr./answer/forex_trading_platform/valuecell/python/start_app.py
#!/usr/bin/env python3
"""
应用启动器 - 在启动前应用 Schema 修复
"""

import os
import sys

# 应用 Schema 修复
try:
    from schema_fix import patch_all_schemas
    if patch_all_schemas():
        print("✅ Schema 修复应用成功")
    else:
        print("⚠️ Schema 修复应用失败，继续启动...")
except ImportError as e:
    print(f"⚠️ 无法加载 Schema 修复: {e}")

# 导入并启动主应用
try:
    # 尝试导入主应用
    from valuecell.app import main
    print("🚀 启动应用...")
    main()
except ImportError:
    try:
        from valuecell.main import main
        print("🚀 启动应用...")
        main()
    except ImportError:
        try:
            # 如果直接运行 python 文件
            import valuecell
            print("🚀 应用已启动")
        except Exception as e:
            print(f"❌ 无法启动应用: {e}")
            sys.exit(1)