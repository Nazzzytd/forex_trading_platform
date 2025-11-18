"""News Agent Core Implementation (Forex Focused)."""

from typing import Any, AsyncGenerator, Dict, Optional

from agno.agent import Agent
from loguru import logger

from valuecell.adapters.models import create_model_for_agent
from valuecell.config.manager import get_config_manager
from valuecell.core.agent.responses import streaming
from valuecell.core.types import BaseAgent, StreamResponse

from .prompts import NEWS_AGENT_INSTRUCTIONS
from .tools import get_breaking_news, get_financial_news, web_search


class NewsAgent(BaseAgent):
    """News Agent for forex market analysis and economic event monitoring."""

    def __init__(self, **kwargs):
        """Initialize the Forex News Agent."""
        super().__init__(**kwargs)
        # Load agent configuration
        self.config_manager = get_config_manager()
        self.agent_config = self.config_manager.get_agent_config("news_agent")

        # Load forex-focused tools
        available_tools = [web_search, get_breaking_news, get_financial_news]

        # Use create_model_for_agent to load agent-specific configuration
        self.knowledge_news_agent = Agent(
            model=create_model_for_agent("news_agent"),
            tools=available_tools,
            instructions=NEWS_AGENT_INSTRUCTIONS,
            markdown=True,  # Enable markdown for better formatting
        )

        logger.info("Forex NewsAgent initialized with economic calendar tools")

    async def stream(
        self,
        query: str,
        conversation_id: str,
        task_id: str,
        dependencies: Optional[Dict] = None,
    ) -> AsyncGenerator[StreamResponse, None]:
        """Stream forex news and analysis responses."""
        logger.info(
            f"Processing forex news query: {query[:100]}{'...' if len(query) > 100 else ''}"
        )

        try:
            # Enhance query for forex context if needed
            enhanced_query = self._enhance_forex_query(query)
            
            response_stream = self.knowledge_news_agent.arun(
                enhanced_query,
                stream=True,
                stream_intermediate_steps=True,
                session_id=conversation_id,
            )
            
            async for event in response_stream:
                if event.event == "RunContent":
                    yield streaming.message_chunk(event.content)
                elif event.event == "ToolCallStarted":
                    yield streaming.tool_call_started(
                        event.tool.tool_call_id, event.tool.tool_name
                    )
                elif event.event == "ToolCallCompleted":
                    yield streaming.tool_call_completed(
                        event.tool.result, event.tool.tool_call_id, event.tool.tool_name
                    )

            yield streaming.done()
            logger.info("Forex news query processed successfully")

        except Exception as e:
            logger.error(f"Error processing forex news query: {str(e)}")
            logger.exception("Full error details:")
            yield {"type": "error", "content": f"Error processing forex news query: {str(e)}"}

    async def run(self, query: str, **kwargs) -> str:
        """Run forex news agent and return analysis response."""
        logger.info(
            f"Running forex news agent with query: {query[:100]}{'...' if len(query) > 100 else ''}"
        )

        try:
            logger.debug("Starting forex news agent processing")

            # Enhance query for better forex analysis
            enhanced_query = self._enhance_forex_query(query)
            
            # Get the complete response from the knowledge news agent
            response = await self.knowledge_news_agent.arun(enhanced_query)

            logger.info("Forex news agent query completed successfully")
            logger.debug(f"Response length: {len(str(response.content))} characters")

            return response.content

        except Exception as e:
            logger.error(f"Error in Forex NewsAgent run: {e}")
            logger.exception("Full error details:")
            return f"Error processing forex news query: {str(e)}"

    def _enhance_forex_query(self, query: str) -> str:
        """Enhance query with forex context when appropriate."""
        query_lower = query.lower()
        
        # Add forex context for general market queries
        forex_keywords = ['market', 'trading', 'currency', 'forex', 'fx', 'usd', 'eur', 'gbp', 'jpy']
        economic_keywords = ['economic', 'news', 'event', 'data', 'rate', 'inflation']
        
        has_forex_context = any(keyword in query_lower for keyword in forex_keywords + economic_keywords)
        
        if has_forex_context and not any(pair in query.upper() for pair in ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']):
            # Add multi-currency context for general market queries
            return f"{query} - 请提供主要货币对(EUR/USD, GBP/USD, USD/JPY等)的外汇市场分析"
        
        return query

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities with forex focus."""
        logger.debug("Retrieving forex news agent capabilities")

        capabilities = {
            "name": "Forex News Agent",
            "description": "Specialized agent for forex market analysis, economic calendar events, and trading insights",
            "tools": [
                {
                    "name": "web_search",
                    "description": "Comprehensive forex trading analysis and multi-currency pair research",
                },
                {
                    "name": "get_breaking_news",
                    "description": "Get urgent forex market updates and high-impact economic events",
                },
                {
                    "name": "get_financial_news",
                    "description": "Get detailed forex market analysis and currency-specific news",
                },
            ],
            "supported_queries": [
                "外汇市场分析",
                "经济日历事件",
                "货币对交易建议", 
                "市场情绪分析",
                "央行政策影响",
                "技术分析水平",
                "多货币对比较",
                "风险管理和仓位建议"
            ],
            "supported_currency_pairs": [
                "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
                "AUD/USD", "USD/CAD", "NZD/USD"
            ],
            "analysis_features": [
                "市场情绪分析",
                "经济事件影响评估", 
                "交易建议生成",
                "风险管理指导",
                "技术位分析",
                "多时间框架分析"
            ]
        }

        logger.debug("Forex capabilities retrieved successfully")
        return capabilities

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of forex news agent."""
        try:
            from .tools import get_economic_calendar
            calendar = get_economic_calendar()
            if calendar:
                health = calendar.health_check()
                return {
                    "status": "operational",
                    "economic_calendar": health,
                    "tools_available": True,
                    "last_updated": "current"
                }
        except Exception as e:
            logger.warning(f"Health check partially failed: {e}")
        
        return {
            "status": "degraded",
            "economic_calendar": "unavailable",
            "tools_available": False,
            "last_updated": "current"
        }