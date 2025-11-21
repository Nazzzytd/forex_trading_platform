# 更新 /Users/fr./answer/forex_trading_platform/valuecell/python/agno_patch.py

import sys
import agno.agent
import logging

logger = logging.getLogger(__name__)

def apply_global_patches():
    """应用全局补丁"""
    print("🔧 APPLYING AGNO PATCHES - ULTIMATE VERSION")
    
    # 补丁 Agno Agent
    original_init = agno.agent.Agent.__init__
    
    count = [0]  # 使用列表来绕过闭包限制
    
    def ultimate_patch(self, *args, **kwargs):
        count[0] += 1
        print(f"🎯 Agno Agent created (#{count[0]})")
        
        # 检查 output_schema
        if 'output_schema' in kwargs:
            schema = kwargs['output_schema']
            schema_name = getattr(schema, '__name__', str(schema))
            print(f"🚨 FOUND output_schema: {schema_name}")
            
            if 'PlannerResponse' in schema_name:
                print(f"💥💥💥 BLOCKING PlannerResponse 💥💥💥")
                import traceback
                print("CREATION STACK:")
                for i, line in enumerate(traceback.format_stack()[-6:-1]):
                    print(f"  {i}: {line.strip()}")
                print("=" * 60)
                
                # 移除有问题的 schema
                kwargs.pop('output_schema', None)
                print("✅ REMOVED PlannerResponse output_schema")
        
        return original_init(self, *args, **kwargs)
    
    agno.agent.Agent.__init__ = ultimate_patch
    print("✅ Ultimate Agno patch applied")

# 自动应用
apply_global_patches()