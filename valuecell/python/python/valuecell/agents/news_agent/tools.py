"""News-related tools for the News Agent (Forex Focused)."""

import os
import sys
from typing import Optional
from agno.agent import Agent
from loguru import logger

from valuecell.adapters.models import create_model

# 使用绝对路径导入 EconomicCalendar
try:
    # 直接使用绝对路径
    absolute_src_path = "/Users/fr./answer/forex_trading_platform/src"
    if absolute_src_path not in sys.path:
        sys.path.insert(0, absolute_src_path)
        logger.info(f"添加 EconomicCalendar 绝对路径: {absolute_src_path}")
    
    from servers.economic_calendar.economic_calendar import EconomicCalendar
    logger.info("✅ EconomicCalendar 导入成功")
    
except ImportError as e:
    logger.error(f"❌ EconomicCalendar 导入失败: {e}")
    
    # 创建模拟实现
    class MockEconomicCalendar:
        def __init__(self):
            logger.warning("使用模拟 EconomicCalendar")
            
        def get_trading_analysis(self, days_ahead=3, currency_pair=None, include_fundamental_analysis=True):
            return {
                "success": True,
                "currency_pair": currency_pair or "多货币对",
                "market_context": {
                    "overall_sentiment": "模拟-中性",
                    "key_market_themes": ["模拟数据", "测试模式"],
                    "volatility_outlook": "模拟-中等"
                },
                "economic_calendar_analysis": {
                    "high_impact_events": 2,
                    "events": [
                        {"event_name": "模拟经济事件1", "actual_value": "100"},
                        {"event_name": "模拟经济事件2", "actual_value": "200"}
                    ]
                },
                "trading_recommendation": {
                    "overall_bias": "模拟-观望",
                    "confidence_level": "模拟-中等",
                    "key_risk_factors": ["模拟风险因素"]
                }
            }
            
        def health_check(self):
            return {
                "success": True,
                "status": "模拟模式",
                "message": "使用模拟数据"
            }
    
    EconomicCalendar = MockEconomicCalendar
    logger.warning("🎭 使用模拟 EconomicCalendar 继续运行")

# Create Economic Calendar instance (Singleton pattern)
_economic_calendar = None

def get_economic_calendar():
    """Get the Economic Calendar instance (Singleton)"""
    global _economic_calendar
    if _economic_calendar is None:
        _economic_calendar = EconomicCalendar()
    return _economic_calendar

async def web_search(query: str) -> str:
    """
    Search web for the given query, specifically tailored for Forex analysis.
    The query is used to trigger a multi-currency pair trading analysis.
    """
    # Use your existing EconomicCalendar for search analysis, focusing on Forex.
    try:
        calendar = get_economic_calendar()
        
        # Foreign exchange-related query, use multi-currency pair analysis
        # days_ahead=2 provides a short-term outlook.
        analysis = calendar.get_trading_analysis(
            days_ahead=2, 
            include_fundamental_analysis=True
        )
        return _format_forex_analysis(analysis)
            
    except Exception as e:
        logger.error(f"web_search failed: {e}")
        return f"搜索失败: {str(e)}"

async def get_breaking_news() -> str:
    """Get breaking news and urgent updates focused on the Forex market."""
    try:
        calendar = get_economic_calendar()
        
        # Use health check to verify service status
        health = calendar.health_check()
        if not health.get("success", True):
            return "经济日历服务暂时不可用"
        
        # Get the latest market analysis (Forex focused)
        analysis = calendar.get_trading_analysis(
            days_ahead=1, # Focusing on immediate/next day events
            include_fundamental_analysis=True
        )
        
        if not analysis.get("success"):
            return f"获取突发新闻失败: {analysis.get('error', '未知错误')}"
        
        # Format the output
        return _format_breaking_news(analysis)
        
    except Exception as e:
        logger.error(f"get_breaking_news failed: {e}")
        return f"获取突发新闻失败: {str(e)}"

async def get_financial_news(
    currency_pair: Optional[str] = None
) -> str:
    """
    Get financial and market news, specifically for a currency pair.
    
    Args:
        currency_pair: Optional currency pair (e.g., 'EUR/USD') to focus the analysis.
    """
    try:
        calendar = get_economic_calendar()
        
        # Get financial analysis
        analysis = calendar.get_trading_analysis(
            currency_pair=currency_pair,
            days_ahead=3, # Longer term outlook for general news
            include_fundamental_analysis=True
        )
        
        if not analysis.get("success"):
            return f"获取金融新闻失败: {analysis.get('error', '未知错误')}"
        
        # Format the output
        return _format_financial_news(analysis, currency_pair)
        
    except Exception as e:
        logger.error(f"get_financial_news failed: {e}")
        return f"获取金融新闻失败: {str(e)}"

# --- Removed _map_to_currency_pair as it was stock-focused ---

def _format_breaking_news(analysis: dict) -> str:
    """格式化突发新闻输出"""
    market_context = analysis.get("market_context", {})
    economic_analysis = analysis.get("economic_calendar_analysis", {})
    
    output = "🚨 突发新闻和市场动态 (外汇)\n\n"
    
    # 市场情绪
    sentiment = market_context.get("overall_sentiment", "未知")
    output += f"📊 市场情绪: {sentiment}\n"
    
    # 关键主题
    themes = market_context.get("key_market_themes", [])
    if themes:
        output += f"🎯 关键主题: {', '.join(themes)}\n"
    
    # 高影响事件
    high_impact = economic_analysis.get("high_impact_events", 0)
    if high_impact > 0:
        output += f"⚠️ 高影响事件: {high_impact}个\n"
    
    # 波动性展望
    volatility = market_context.get("volatility_outlook", "未知")
    output += f"📈 波动性展望: {volatility}\n\n"
    
    # 交易建议摘要
    trading_rec = analysis.get("trading_recommendation", {})
    if trading_rec:
        output += "💡 交易建议摘要:\n"
        output += f"    总体偏向: {trading_rec.get('overall_bias', '未知')}\n"
        output += f"    主要风险: {trading_rec.get('key_risk_factors', ['未知'])[0]}\n"
    
    return output

def _format_financial_news(analysis: dict, currency_pair: Optional[str]) -> str:
    """格式化金融新闻输出"""
    market_context = analysis.get("market_context", {})
    economic_analysis = analysis.get("economic_calendar_analysis", {})
    trading_rec = analysis.get("trading_recommendation", {})
    
    # 标题
    if currency_pair:
        title = f"💱 {currency_pair} 外汇分析"
    else:
        title = "📊 总体外汇市场新闻"
    
    output = f"{title}\n\n"
    
    # 市场概况
    output += "📊 市场概况\n"
    output += f"    情绪: {market_context.get('overall_sentiment', '未知')}\n"
    output += f"    主题: {', '.join(market_context.get('key_market_themes', []))}\n"
    output += f"    波动性: {market_context.get('volatility_outlook', '未知')}\n\n"
    
    # 经济事件
    events = economic_analysis.get("events", [])
    if events:
        output += "📅 最新经济数据\n"
        for i, event in enumerate(events[:3], 1):
            output += f"    {i}. {event.get('event_name', '未知')}: {event.get('actual_value', 'N/A')}\n"
        output += "\n"
    
    # 交易建议
    if trading_rec:
        output += "💡 交易建议\n"
        output += f"    操作: {trading_rec.get('overall_bias', '未知')}\n"
        
        actions = trading_rec.get("recommended_actions", [])
        if actions:
            action = actions[0]
            output += f"    时间框架: {action.get('timeframe', '未知')}\n"
            output += f"    风险等级: {action.get('risk_level', '未知')}\n"
    
    return output

def _format_forex_analysis(analysis: dict) -> str:
    """格式化外汇分析输出"""
    if "individual_analyses" in analysis:
        # Multi-currency pair analysis
        return _format_multi_currency_analysis(analysis)
    else:
        # Single currency pair analysis
        return _format_single_currency_analysis(analysis)

def _format_multi_currency_analysis(analysis: dict) -> str:
    """格式化多货币对分析"""
    individual_analyses = analysis.get("individual_analyses", {})
    summary = analysis.get("summary", {})
    
    output = "🌍 多货币对市场分析\n\n"
    
    # Summary
    output += "📈 市场概览\n"
    output += f"    看涨货币对: {', '.join(summary.get('bullish_pairs', []))}\n"
    output += f"    看跌货币对: {', '.join(summary.get('bearish_pairs', []))}\n"
    output += f"    整体偏向: {summary.get('dominant_bias', '中性')}\n\n"
    
    # Detailed Analysis (Top 3)
    output += "💱 主要货币对分析 (前3)\n"
    for i, (pair, pair_analysis) in enumerate(list(individual_analyses.items())[:3], 1):
        if pair_analysis.get("success"):
            trading_rec = pair_analysis.get("trading_recommendation", {})
            output += f"{i}. {pair}: {trading_rec.get('overall_bias', '未知')}\n"
    
    return output

def _format_single_currency_analysis(analysis: dict) -> str:
    """格式化单货币对分析"""
    currency_pair = analysis.get("currency_pair", "未知")
    trading_rec = analysis.get("trading_recommendation", {})
    market_context = analysis.get("market_context", {})
    
    output = f"💱 {currency_pair} 详细分析\n\n"
    
    output += "📊 市场环境\n"
    output += f"    情绪: {market_context.get('overall_sentiment', '未知')}\n"
    output += f"    波动性: {market_context.get('volatility_outlook', '未知')}\n\n"
    
    output += "💡 交易建议\n"
    output += f"    操作: {trading_rec.get('overall_bias', '未知')}\n"
    
    actions = trading_rec.get("recommended_actions", [])
    if actions:
        for action in actions[:2]:
            output += f"    • {action.get('timeframe', '')}: {action.get('action', '')} ({action.get('risk_level', '')}风险)\n"
    
    return output