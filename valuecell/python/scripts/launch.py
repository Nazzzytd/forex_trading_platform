"""
Interactive agent launcher script.
Allows users to select an agent from available options and launch it using uv.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict
import sys
import importlib

print("💥 FORCE START WITH CLEAN CACHE")

# 禁用字节码生成
sys.dont_write_bytecode = True

# 强制路径
sys.path.insert(0, '/Users/fr./answer/forex_trading_platform/valuecell/python')

print("🔍 STARTING WITH RUNTIME MONITORING")

# 1. 首先创建并启动运行时监控
try:
    # 创建监控类
    import threading
    import time
    
    class RuntimeMonitor:
        def __init__(self):
            self.agent_creations = []
            self.monitoring = False
        
        def start_monitoring(self):
            self.monitoring = True
            print("🎯 RUNTIME MONITOR: Started monitoring Agent creations")
            
            def monitor_loop():
                while self.monitoring:
                    if self.agent_creations:
                        print(f"📊 MONITOR: {len(self.agent_creations)} Agent creations detected")
                        for i, creation in enumerate(self.agent_creations[-3:]):
                            print(f"  {i}: Schema={creation['schema']}")
                    time.sleep(3)  # 每3秒检查一次
            
            threading.Thread(target=monitor_loop, daemon=True).start()
        
        def log_agent_creation(self, schema_name):
            if self.monitoring:
                self.agent_creations.append({
                    'time': time.time(),
                    'schema': schema_name
                })
                print(f"🎯 MONITOR: Agent created with schema: {schema_name}")
    
    # 创建全局监控实例
    monitor = RuntimeMonitor()
    
    # 补丁 Agno Agent 来使用监控
    import agno.agent
    original_init = agno.agent.Agent.__init__
    
    def monitored_init(self, *args, **kwargs):
        # 记录所有 Agent 创建，无论是否有 output_schema
        print(f"🎯 MONITOR: Agent.__init__ called")
        print(f"🎯 MONITOR: Args keys: {list(kwargs.keys())}")
        
        # 记录调用堆栈
        import traceback
        stack = traceback.format_stack()[-4:-1]  # 最近3个堆栈帧
        print(f"🎯 MONITOR: Call stack:")
        for line in stack:
            if 'valuecell' in line or 'agno' in line:
                print(f"  {line.strip()}")
        
        if 'output_schema' in kwargs:
            schema = kwargs['output_schema']
            schema_name = getattr(schema, '__name__', str(schema))
            
            print(f"🎯 MONITOR: Found output_schema: {schema_name}")
            monitor.log_agent_creation(schema_name)
            
            if 'PlannerResponse' in schema_name:
                print(f"💥 RUNTIME BLOCK: PlannerResponse detected and blocked!")
                kwargs.pop('output_schema', None)
        else:
            print(f"🎯 MONITOR: No output_schema provided")
        
        return original_init(self, *args, **kwargs)
    
    agno.agent.Agent.__init__ = monitored_init
    
    # 启动监控
    monitor.start_monitoring()
    print("✅ Runtime monitor started successfully")
    
    # 验证补丁是否生效
    print("🔍 VERIFYING MONITOR PATCH...")
    print(f"✅ Agno Agent patched: {agno.agent.Agent.__init__.__name__}")
    
    # 测试创建一个简单的 Agent 来验证监控
    try:
        print("🧪 Creating test Agent to verify monitor...")
        test_agent = agno.agent.Agent(model="test-model")
        print("✅ Test Agent created - monitor is working!")
    except Exception as e:
        print(f"❌ Test Agent creation failed: {e}")
    
except Exception as e:
    print(f"❌ Runtime monitor failed: {e}")
    import traceback
    traceback.print_exc()

# 原有的 launch.py 代码继续...
import questionary


# Mapping from agent name to analyst key (for ai-hedge-fund agents)
MAP_NAME_ANALYST: Dict[str, str] = {
    "AswathDamodaranAgent": "aswath_damodaran",
    "BenGrahamAgent": "ben_graham",
    "BillAckmanAgent": "bill_ackman",
    "CathieWoodAgent": "cathie_wood",
    "CharlieMungerAgent": "charlie_munger",
    "FundamentalsAnalystAgent": "fundamentals_analyst",
    "MichaelBurryAgent": "michael_burry",
    "MohnishPabraiAgent": "mohnish_pabrai",
    "PeterLynchAgent": "peter_lynch",
    "PhilFisherAgent": "phil_fisher",
    "RakeshJhunjhunwalaAgent": "rakesh_jhunjhunwala",
    "SentimentAnalystAgent": "sentiment_analyst",
    "StanleyDruckenmillerAgent": "stanley_druckenmiller",
    "TechnicalAnalystAgent": "technical_analyst",
    "ValuationAnalystAgent": "valuation_analyst",
    "WarrenBuffettAgent": "warren_buffett",
}
TRADING_AGENTS_NAME = "TradingAgents"
RESEARCH_AGENT_NAME = "ResearchAgent"
AUTO_TRADING_AGENT_NAME = "AutoTradingAgent"
NEWS_AGENT_NAME = "NewsAgent"
STRATEGY_AGENT_NAME = "StrategyAgent"
# AGENTS = list(MAP_NAME_ANALYST.keys()) + [
#     TRADING_AGENTS_NAME,
#     RESEARCH_AGENT_NAME,
#     AUTO_TRADING_AGENT_NAME,
# ]
AGENTS = [
    RESEARCH_AGENT_NAME,
    AUTO_TRADING_AGENT_NAME,
    NEWS_AGENT_NAME,
    STRATEGY_AGENT_NAME,
]

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
PYTHON_DIR = PROJECT_DIR / "python"
ENV_PATH = PROJECT_DIR / ".env"

# Convert paths to POSIX format (forward slashes) for cross-platform compatibility
# as_posix() works on both Windows and Unix systems
PROJECT_DIR_STR = PROJECT_DIR.as_posix()
PYTHON_DIR_STR = PYTHON_DIR.as_posix()
ENV_PATH_STR = ENV_PATH.as_posix()

AUTO_TRADING_ENV_OVERRIDES = {
    "AUTO_TRADING_EXCHANGE": os.getenv("AUTO_TRADING_EXCHANGE"),
}
AUTO_TRADING_ENV_PREFIX = " ".join(
    f"{key}={value}"
    for key, value in AUTO_TRADING_ENV_OVERRIDES.items()
    if value not in (None, "")
)
if AUTO_TRADING_ENV_PREFIX:
    AUTO_TRADING_ENV_PREFIX = f"{AUTO_TRADING_ENV_PREFIX} "

# Mapping from agent name to launch command
MAP_NAME_COMMAND: Dict[str, str] = {}
# Remove external agent entries
# for name, analyst in MAP_NAME_ANALYST.items():
#     MAP_NAME_COMMAND[name] = (
#         f"uv run --env-file {ENV_PATH_STR} -m adapter --analyst {analyst}"
#     )
# MAP_NAME_COMMAND[TRADING_AGENTS_NAME] = (
#     f"uv run --env-file {ENV_PATH_STR} -m adapter"
# )
# Keep only first-party agents
MAP_NAME_COMMAND[RESEARCH_AGENT_NAME] = (
    f"uv run --env-file {ENV_PATH_STR} -m valuecell.agents.research_agent"
)
MAP_NAME_COMMAND[AUTO_TRADING_AGENT_NAME] = (
    f"{AUTO_TRADING_ENV_PREFIX}uv run --env-file {ENV_PATH_STR} -m valuecell.agents.auto_trading_agent"
)
MAP_NAME_COMMAND[NEWS_AGENT_NAME] = (
    f"uv run --env-file {ENV_PATH_STR} -m valuecell.agents.news_agent"
)
MAP_NAME_COMMAND[STRATEGY_AGENT_NAME] = (
    f"uv run --env-file {ENV_PATH_STR} -m valuecell.agents.strategy_agent"
)
BACKEND_COMMAND = (
    f"cd {PYTHON_DIR_STR} && uv run --env-file {ENV_PATH_STR} -m valuecell.server.main"
)
FRONTEND_URL = "http://localhost:1420"


def check_envfile_is_set():
    if not ENV_PATH.exists():
        print(
            f".env file not found at {ENV_PATH}. Please create it with necessary environment variables. "
            "check python/.env.example for reference."
        )
        exit(1)


def main():
    check_envfile_is_set()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = f"{PROJECT_DIR_STR}/logs/{timestamp}"

    # Use questionary multi-select to allow choosing multiple agents
    # selected_agents = questionary.checkbox(
    #     "Choose agents to launch (use space to select, enter to confirm):",
    #     choices=AGENTS,
    # ).ask()
    selected_agents = AGENTS

    if not selected_agents:
        print("No agents selected.")
        exit(1)

    os.makedirs(log_dir, exist_ok=True)
    print(f"Logs will be saved to {log_dir}/")

    processes = []
    logfiles = []
    for selected_agent in selected_agents:
        logfile_path = f"{log_dir}/{selected_agent}.log"
        print(f"Starting agent: {selected_agent} - output to {logfile_path}")

        # Open logfile for writing
        logfile = open(logfile_path, "w")
        logfiles.append(logfile)

        # Launch command using Popen with output redirected to logfile
        process = subprocess.Popen(
            MAP_NAME_COMMAND[selected_agent], shell=True, stdout=logfile, stderr=logfile
        )
        processes.append(process)
    print("All agents launched. Waiting for tasks...")

    for selected_agent in selected_agents:
        print(
            f"You can monitor {selected_agent} logs at {log_dir}/{selected_agent}.log or chat on: {FRONTEND_URL}/agent/{selected_agent}"
        )

    # Launch backend
    logfile_path = f"{log_dir}/backend.log"
    print(f"Starting backend - output to {logfile_path}")
    print(f"Frontend available at {FRONTEND_URL}")
    logfile = open(logfile_path, "w")
    logfiles.append(logfile)
    process = subprocess.Popen(
        BACKEND_COMMAND, shell=True, stdout=logfile, stderr=logfile
    )
    processes.append(process)

    for process in processes:
        process.wait()
    for logfile in logfiles:
        logfile.close()
    print(f"All agents finished. Check {log_dir}/ for output.")


if __name__ == "__main__":
    main()
