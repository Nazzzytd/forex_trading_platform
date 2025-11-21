# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/safe_agent.py

from agno.agent import Agent as OriginalAgent

def SafeAgent(*args, **kwargs):
    """安全的 Agent 创建函数，自动阻止 PlannerResponse"""
    
    # 检查并修复 output_schema
    if 'output_schema' in kwargs:
        schema = kwargs['output_schema']
        schema_name = getattr(schema, '__name__', str(schema))
        
        if 'PlannerResponse' in schema_name:
            print(f"💥 SAFE AGENT: Blocking PlannerResponse")
            kwargs.pop('output_schema', None)
    
    # 创建 Agent
    return OriginalAgent(*args, **kwargs)

# 替换原始的 Agent
import agno.agent
agno.agent.Agent = SafeAgent
print("✅ Safe Agent factory installed")