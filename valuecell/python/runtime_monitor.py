# 创建 /Users/fr./answer/forex_trading_platform/valuecell/python/runtime_monitor.py

import sys
import threading
import time

class RuntimeMonitor:
    def __init__(self):
        self.agent_creations = []
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控 Agent 创建"""
        self.monitoring = True
        print("🔍 RUNTIME MONITOR: Started monitoring Agent creations")
        
        # 监控线程
        def monitor_loop():
            while self.monitoring:
                if self.agent_creations:
                    print(f"📊 MONITOR: {len(self.agent_creations)} Agent creations detected")
                    for i, creation in enumerate(self.agent_creations[-3:]):  # 显示最近3个
                        print(f"  {i}: {creation}")
                time.sleep(2)
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def log_agent_creation(self, schema_name, stack_trace):
        """记录 Agent 创建"""
        if self.monitoring:
            self.agent_creations.append({
                'time': time.time(),
                'schema': schema_name,
                'stack': stack_trace[-3:]  # 只保存最后3行堆栈
            })
            print(f"🎯 MONITOR: Agent created with schema: {schema_name}")

# 全局监控实例
monitor = RuntimeMonitor()

# 补丁 Agno Agent 来使用监控
import agno.agent
original_init = agno.agent.Agent.__init__

def monitored_init(self, *args, **kwargs):
    if 'output_schema' in kwargs:
        schema = kwargs['output_schema']
        schema_name = getattr(schema, '__name__', str(schema))
        
        # 记录到监控
        import traceback
        monitor.log_agent_creation(schema_name, traceback.format_stack())
        
        # 如果是 PlannerResponse，阻止
        if 'PlannerResponse' in schema_name:
            print(f"💥 RUNTIME BLOCK: PlannerResponse detected and blocked")
            kwargs.pop('output_schema', None)
    
    return original_init(self, *args, **kwargs)

agno.agent.Agent.__init__ = monitored_init

# 启动监控
monitor.start_monitoring()
print("✅ Runtime monitor started")