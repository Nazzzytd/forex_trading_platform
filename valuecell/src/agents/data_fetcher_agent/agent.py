import sys
import os
from typing import Dict, Any  # 确保导入 Any

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../..')
sys.path.insert(0, project_root)

from agents.base.forex_agent import ForexAgent

class DataFetcherAgent(ForexAgent):
    """数据获取Agent - 包装现有的DataFetcher"""
    
    def __init__(self):
        super().__init__(
            name="data_fetcher",
            description="外汇实时数据获取Agent"
        )
        self._fetcher = None
    
    @property
    def fetcher(self):
        """懒加载现有的DataFetcher"""
        if self._fetcher is None:
            try:
                # 使用绝对导入
                from servers.data_fetcher.data_fetcher import DataFetcher
                self._fetcher = DataFetcher()
                print(f"✅ DataFetcher加载成功")
            except ImportError as e:
                print(f"❌ DataFetcher导入失败: {e}")
                # 尝试相对导入
                try:
                    import importlib.util
                    data_fetcher_path = os.path.join(project_root, 'src/servers/data_fetcher/data_fetcher.py')
                    spec = importlib.util.spec_from_file_location("data_fetcher", data_fetcher_path)
                    data_fetcher_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(data_fetcher_module)
                    self._fetcher = data_fetcher_module.DataFetcher()
                    print(f"✅ DataFetcher通过文件加载成功")
                except Exception as e2:
                    print(f"❌ DataFetcher文件加载也失败: {e2}")
                    raise
                
        return self._fetcher
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据获取任务"""
        try:
            # 参数解析 - 保持与你原有接口兼容
            currency_pair = task.get("currency_pair") or task.get("symbol", "EUR/USD")
            data_type = task.get("data_type", "realtime")
            interval = task.get("interval") or task.get("timeframe", "1h")
            output_size = task.get("output_size", 100)
            
            print(f"🔹 DataFetcherAgent 获取 {currency_pair} {data_type} 数据...")
            
            # 调用原有的DataFetcher方法
            result = self.fetcher.fetch_data(
                currency_pair=currency_pair,
                data_type=data_type,
                interval=interval,
                output_size=output_size
            )
            
            # 确保返回格式统一
            if result.get("success", False):
                return {
                    "success": True,
                    "agent": self.name,
                    "data_type": data_type,
                    "currency_pair": currency_pair,
                    "interval": interval,
                    "data": result.get("data", {}),
                    "metadata": result.get("metadata", {}),
                    "summary": result.get("summary", {}),
                    "timestamp": "2024-01-01T00:00:00Z"  # 实际应该用datetime.now()
                }
            else:
                return {
                    "success": False,
                    "agent": self.name,
                    "error": result.get("error", "数据获取失败"),
                    "currency_pair": currency_pair,
                    "data_type": data_type
                }
            
        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": f"DataFetcherAgent执行异常: {str(e)}",
                "currency_pair": task.get("currency_pair", "unknown"),
                "data_type": task.get("data_type", "unknown")
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            health_result = self.fetcher.health_check()
            return {
                "success": health_result.get("success", False),
                "agent": self.name,
                "status": health_result.get("status", "unknown"),
                "api_connected": health_result.get("api_connected", False),
                "message": health_result.get("message", ""),
                "error": health_result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": f"健康检查失败: {str(e)}"
            }
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            stats = self.fetcher.get_usage_stats()
            return {
                "success": stats.get("success", False),
                "agent": self.name,
                "daily_requests_used": stats.get("daily_requests_used", 0),
                "daily_requests_remaining": stats.get("daily_requests_remaining", 0),
                "status": stats.get("status", "unknown"),
                "error": stats.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": f"获取统计失败: {str(e)}"
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """返回Agent的能力描述"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": [
                "fetch_realtime_data",
                "fetch_historical_data", 
                "fetch_intraday_data",
                "batch_fetch",
                "health_check",
                "usage_stats"
            ],
            "supported_data_types": ["realtime", "historical", "intraday"],
            "supported_intervals": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            "input_parameters": {
                "currency_pair": "string (e.g., EUR/USD)",
                "data_type": "string (realtime/historical/intraday)",
                "interval": "string (timeframe)",
                "output_size": "integer"
            }
        }
