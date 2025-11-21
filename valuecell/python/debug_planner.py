# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/debug_planner.py

import sys
sys.path.insert(0, '/Users/fr./answer/forex_trading_platform/valuecell/python')

def find_planner_usage():
    """找到所有使用 PlannerResponse 的地方"""
    import ast
    import os
    
    planner_files = []
    
    for root, dirs, files in os.walk('/Users/fr./answer/forex_trading_platform'):
        for file in files:
            if file.endswith('.py') and '__pycache__' not in root:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'PlannerResponse' in content:
                            planner_files.append(filepath)
                            print(f"📄 Found PlannerResponse in: {filepath}")
                except:
                    pass
    
    return planner_files

print("🔍 Searching for PlannerResponse usage...")
files = find_planner_usage()
print(f"📋 Found {len(files)} files using PlannerResponse")
for f in files:
    print(f"  - {f}")