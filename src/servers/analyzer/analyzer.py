# servers/analyzer/analyzer.py
import json
import os
import logging
import numpy as np
from typing import Dict, Any, Optional, List
from openai import OpenAI
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Analyzer:
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 openai_base_url: Optional[str] = None,
                 default_model: str = "gpt-4"):
        """
        初始化综合分析器
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_BASE_URL")
        self.default_model = default_model
        self.client = None
        
        # 初始化OpenAI客户端
        if self.openai_api_key:
            try:
                self.client = OpenAI(
                    api_key=self.openai_api_key,
                    base_url=self.openai_base_url
                )
                logger.info("✅ Analyzer AI客户端初始化成功")
            except Exception as e:
                logger.error(f"❌ Analyzer AI客户端初始化失败: {e}")
        else:
            logger.warning("⚠️ 未提供OpenAI API密钥，AI功能将不可用")
    
    def analyze_user_query(self, user_query: str) -> Dict[str, Any]:
        """
        分析用户输入，识别货币对、问题类型和分析需求
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI客户端未初始化，请检查API密钥配置",
                "analysis": None
            }
        
        try:
            prompt = f"""
请分析以下外汇交易相关的用户查询：

用户查询: "{user_query}"

请从以下维度进行分析：
1. 识别用户提到的具体货币对（如EUR/USD, GBP/JPY等）
2. 分析用户的核心问题和关注点
3. 确定分析的重点方向
4. 提出需要收集的数据类型
5. 给出分析建议

请以JSON格式返回分析结果：
{{
    "identified_currency_pairs": ["货币对1", "货币对2"],
    "primary_currency_pair": "主要货币对",
    "query_type": "趋势分析/技术分析/基本面分析/风险评估/交易机会等",
    "user_concerns": ["用户关注点1", "用户关注点2"],
    "analysis_focus": ["分析重点1", "分析重点2"],
    "required_data": ["市场数据", "经济数据", "技术指标", "新闻情绪等"],
    "analysis_suggestions": ["建议1", "建议2"],
    "complexity_level": "简单/中等/复杂"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system", 
                        "content": """您是专业的外汇市场分析师，擅长理解用户交易相关问题并制定分析计划。
请准确识别货币对，理解用户真实需求，并提供专业的分析建议。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            query_analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "query_analysis": query_analysis,
                "original_query": user_query,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"用户查询分析失败: {e}")
            return {
                "success": False,
                "error": f"查询分析失败: {str(e)}",
                "analysis": None
            }
    
    def generate_comprehensive_analysis(self, 
                                    market_data: Dict[str, Any],
                                    economic_data: Dict[str, Any], 
                                    technical_data: Dict[str, Any],
                                    user_query: str = "",
                                    query_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成综合易读分析报告，包含深度交易建议
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI客户端未初始化，请检查API密钥配置",
                "analysis": None
            }
        
        try:
            # 如果没有提供查询分析，先进行分析
            if not query_analysis and user_query:
                query_result = self.analyze_user_query(user_query)
                if query_result["success"]:
                    query_analysis = query_result["query_analysis"]
            
            # 智能数据提取和分析
            analysis_context = self._prepare_analysis_context(market_data, economic_data, technical_data, user_query, query_analysis)
            
            # 构建动态分析提示 - 增强交易建议部分
            prompt = self._build_dynamic_analysis_prompt(analysis_context)
            
            # 调用AI分析
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system", 
                        "content": """您是顶级外汇交易分析师，擅长综合技术分析、基本面分析和市场情绪分析。
请根据实际可用的数据内容，提供专业、易读、结构清晰的分析报告。
重点分析实际存在的数据，对于缺失的数据要明确说明限制。
特别要基于所有可用指标（经济事件、技术信号、价格数据）给出具体的交易建议。
使用markdown风格的格式，包含具体的价格水平、数据支持和可执行的交易策略。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis_text,
                "query_analysis": query_analysis,
                "data_context": analysis_context["data_availability"],
                "metadata": {
                    "model_used": self.default_model,
                    "user_query": user_query,
                    "data_sources_used": analysis_context["available_sources"],
                    "analysis_timestamp": self._get_timestamp(),
                    "output_format": "readable_text"
                }
            }
            
        except Exception as e:
            logger.error(f"综合分析生成失败: {e}")
            return {
                "success": False,
                "error": f"分析生成失败: {str(e)}",
                "analysis": None
            }

    
    def _prepare_analysis_context(self, market_data, economic_data, technical_data, user_query, query_analysis):
        """准备分析上下文，识别可用的数据内容和重点"""
        # 提取数据
        market_info = self._extract_market_data(market_data)
        economic_info = self._extract_economic_data(economic_data)
        technical_info = self._extract_technical_data(technical_data)
        
        # 分析数据可用性和内容特点
        context = {
            "user_query": user_query,
            "query_analysis": query_analysis,
            "market_data": market_info,
            "economic_data": economic_info,
            "technical_data": technical_info,
            "data_availability": self._analyze_data_availability(market_info, economic_info, technical_info),
            "analysis_focus": self._determine_analysis_focus(market_info, economic_info, technical_info, query_analysis),
            "available_sources": []
        }
        
        # 确定可用数据源
        if context["data_availability"]["has_market_data"]:
            context["available_sources"].append("market")
        if context["data_availability"]["has_economic_data"]:
            context["available_sources"].append("economic")
        if context["data_availability"]["has_technical_data"]:
            context["available_sources"].append("technical")
            
        return context
    
    def _analyze_data_availability(self, market_info, economic_info, technical_info):
        """分析数据可用性"""
        return {
            "has_market_data": bool(market_info.get("price")),
            "has_economic_data": bool(economic_info.get("sentiment") or economic_info.get("events")),
            "has_technical_data": bool(technical_info.get("signals") or technical_info.get("indicators")),
            "market_data_type": market_info.get("metadata", {}).get("data_type"),
            "economic_data_type": "multi_currency" if economic_info.get("analysis_type") == "multi_currency" else "single_currency",
            "technical_data_type": technical_info.get("data_type")
        }
    
    def _determine_analysis_focus(self, market_info, economic_info, technical_info, query_analysis):
        """根据实际数据确定分析重点"""
        focus_areas = []
        
        # 根据查询分析确定基础重点
        if query_analysis:
            focus_areas.extend(query_analysis.get("analysis_focus", []))
        
        # 根据数据内容调整重点
        availability = self._analyze_data_availability(market_info, economic_info, technical_info)
        
        if availability["has_technical_data"]:
            if technical_info.get("data_type") == "trading_signals":
                focus_areas.append("交易信号分析")
                focus_areas.append("技术指标一致性")
            elif technical_info.get("data_type") == "technical_indicators":
                focus_areas.append("技术指标深度分析")
                focus_areas.append("价格行为分析")
        
        if availability["has_economic_data"]:
            if economic_info.get("sentiment", {}).get("overall"):
                focus_areas.append("市场情绪影响")
            if economic_info.get("events"):
                focus_areas.append("经济事件分析")
            if availability["economic_data_type"] == "multi_currency":
                focus_areas.append("跨货币对比较分析")
        
        if availability["has_market_data"]:
            if availability["market_data_type"] == "real_time":
                focus_areas.append("实时价格分析")
            elif availability["market_data_type"] == "historical":
                focus_areas.append("历史走势分析")
        
        # 去重并限制数量
        return list(set(focus_areas))[:5]
    
    def _build_dynamic_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """构建动态分析提示，增强交易建议部分"""
        
        availability = context["data_availability"]
        focus_areas = context["analysis_focus"]
        
        prompt_parts = []
        
        # 1. 分析任务描述
        prompt_parts.append(f"""# 外汇深度分析报告生成

## 用户查询
{context['user_query'] or "通用市场分析"}""")

        # 2. 查询分析结果
        if context['query_analysis']:
            prompt_parts.append(f"""
## 查询分析结果
- **主要货币对**: {context['query_analysis'].get('primary_currency_pair', '待识别')}
- **分析重点**: {', '.join(focus_areas)}
- **用户关注**: {', '.join(context['query_analysis'].get('user_concerns', ['市场走势']))}""")

        # 3. 数据可用性报告
        prompt_parts.append(f"""
## 数据可用性报告
{self._format_data_availability_report(availability)}""")

        # 4. 详细数据内容
        prompt_parts.append("""
## 详细数据内容""")
        
        # 根据实际数据添加相应部分
        if availability["has_market_data"]:
            prompt_parts.append(f"""
### 📊 市场数据
{self._format_market_data_for_analysis(context['market_data'])}""")
        
        if availability["has_economic_data"]:
            prompt_parts.append(f"""
### 📈 经济数据与市场情绪
{self._format_economic_data_for_analysis(context['economic_data'])}""")
        
        if availability["has_technical_data"]:
            prompt_parts.append(f"""
### 🔧 技术分析
{self._format_technical_data_for_analysis(context['technical_data'])}""")

        # 5. 分析指令 - 增强交易建议部分
        prompt_parts.append(f"""
## 分析指令

请基于以上实际可用的数据，生成专业的外汇深度分析报告。**特别强调基于具体数据给出可执行的交易建议**。

### 核心分析框架

{self._generate_enhanced_analysis_instructions(availability, focus_areas)}

### 交易建议具体要求

请基于以下可用数据给出**具体的交易策略**：

1. **入场条件**：基于技术信号、价格水平或经济事件的具体触发条件
2. **仓位管理**：根据风险水平和信号强度建议仓位大小
3. **风险控制**：明确的止损位置和风险管理措施
4. **目标价位**：基于技术分析和基本面支持的具体目标
5. **时间框架**：交易的时间周期建议
6. **监控要点**：需要关注的关键事件和价格水平

### 报告格式要求

请按照以下结构组织报告：

## AI 深度分析
───────

### 1. 综合市场评估
[基于所有可用数据的整体市场判断]

### 2. 关键技术信号分析  
[详细的技术指标解读和信号一致性]

### 3. 基本面驱动因素
[经济事件和情绪面对价格的影响]

### 4. 交易策略建议
**[这是重点部分，必须包含具体可执行的交易计划]**

#### 4.1 主要交易机会
- **方向偏好**: 明确看多/看空/中性
- **置信水平**: 基于数据支持的程度
- **核心逻辑**: 交易的主要依据

#### 4.2 具体交易设置
- **入场区域**: 具体价格区间
- **止损位置**: 明确止损价位
- **目标价位**: 分批目标位置
- **仓位建议**: 风险调整后的仓位大小

#### 4.3 替代方案
- 如果主要设置未触发时的备选计划

### 5. 风险与监控
[关键风险因素和需要监控的事件]

**重要**：所有交易建议必须基于前面分析中提到的具体数据支持，避免泛泛而谈。

请开始生成分析报告：""")

        return "\n".join(prompt_parts)
    
    def _generate_enhanced_analysis_instructions(self, availability, focus_areas):
        """生成增强的分析指令，特别关注交易建议"""
        instructions = []
        
        instructions.append("### 1. 综合市场评估")
        
        if availability["has_market_data"]:
            instructions.append("- 📊 **价格分析**: 当前价格、变化趋势、关键水平")
            instructions.append("- 💰 **波动评估**: 基于价格变化的波动性分析")
        
        if availability["has_economic_data"]:
            instructions.append("- 📈 **情绪面**: 市场情绪得分和主要主题")
            instructions.append("- 🗓️ **事件驱动**: 重要经济事件的实际影响")
        
        instructions.append("### 2. 关键技术信号")
        
        if availability["has_technical_data"]:
            if availability["technical_data_type"] == "trading_signals":
                instructions.append("- 🔔 **综合信号**: 交易信号强度和方向")
                instructions.append("- 📉 **指标一致性**: RSI、MACD等指标协同性")
            elif availability["technical_data_type"] == "technical_indicators":
                instructions.append("- 📊 **深度指标**: 关键技术水平分析")
                instructions.append("- 🎯 **趋势确认**: 趋势强度和持续性评估")
        
        instructions.append("### 3. 交易策略制定")
        instructions.append("- 💡 **机会识别**: 基于数据支持的最佳交易时机")
        instructions.append("- ⚖️ **风险回报**: 具体的风险回报比评估")
        instructions.append("- 🛡️ **风控措施**: 基于波动性和支撑阻力的止损设置")
        
        instructions.append("### 4. 执行与监控")
        instructions.append("- 🎯 **具体设置**: 入场、止损、目标的明确价位")
        instructions.append("- 🔄 **动态调整**: 根据市场变化的调整策略")
        instructions.append("- 📱 **监控要点**: 需要重点关注的事件和水平")
        
        # 添加基于特定数据类型的交易建议重点
        if availability["has_economic_data"] and availability["economic_data_type"] == "multi_currency":
            instructions.append("\n### 🌍 跨市场机会")
            instructions.append("- 基于多货币对分析的相对价值机会")
        
        if availability["has_technical_data"] and availability["technical_data_type"] == "trading_signals":
            instructions.append("\n### ⚡ 信号驱动策略")
            instructions.append("- 基于复合交易信号的时机选择")
        
        return "\n".join(instructions)

    # 数据格式化方法 - 针对分析优化
    def _format_market_data_for_analysis(self, market_data):
        """格式化市场数据用于分析"""
        if not market_data.get("price"):
            return "无有效的市场价格数据"
        
        lines = []
        price = market_data["price"]
        
        # 价格信息
        current_price = price.get('exchange_rate') or price.get('close')
        if current_price:
            lines.append(f"- **当前价格**: {current_price}")
        
        if price.get('change') and price.get('percent_change'):
            change_dir = "📈" if float(price.get('change', 0)) > 0 else "📉"
            lines.append(f"- **价格变化**: {change_dir} {price['change']} ({price['percent_change']}%)")
        
        if price.get('volume'):
            lines.append(f"- **交易量**: {price['volume']}")
        
        # 货币对信息
        currency_info = market_data.get("currency_info", {})
        if currency_info.get('pair'):
            lines.append(f"- **分析标的**: {currency_info['pair']}")
        
        return "\n".join(lines)
    
    def _format_economic_data_for_analysis(self, economic_data):
        """格式化经济数据用于分析 - 增强交易相关信息"""
        if not economic_data:
            return "无经济数据可用"
        
        lines = []
        
        # 市场情绪
        sentiment = economic_data.get("sentiment", {})
        if sentiment.get("overall"):
            sentiment_emoji = "🐂" if "涨" in sentiment["overall"] else "🐻" if "跌" in sentiment["overall"] else "⚖️"
            lines.append(f"- **市场情绪**: {sentiment_emoji} {sentiment['overall']}")
            if sentiment.get("score"):
                confidence = "高" if sentiment['score'] > 70 else "低" if sentiment['score'] < 30 else "中"
                lines.append(f"- **情绪强度**: {sentiment['score']}/100 ({confidence}置信度)")
        
        # 关键主题
        key_themes = sentiment.get("key_themes", [])
        if key_themes:
            lines.append(f"- **市场主题**: {', '.join(key_themes[:3])}")
        
        # 经济事件 - 重点关注高影响事件
        events = economic_data.get("events", [])
        high_impact_events = [e for e in events if e.get("importance") == "高"]
        
        if high_impact_events:
            lines.append(f"- **高影响事件**: {len(high_impact_events)}个待关注")
            for event in high_impact_events[:3]:  # 显示最重要的3个事件
                status_emoji = "🟢" if event.get("status") == "已发布" else "🟡" if event.get("status") == "进行中" else "🔴"
                actual_info = f"实际值: {event.get('actual')}" if event.get('actual') else "待发布"
                lines.append(f"  - {status_emoji} {event.get('name')}: {actual_info}")
        
        # 交易建议 - 增强显示
        recommendation = economic_data.get("recommendation", {})
        if recommendation.get("bias"):
            bias_emoji = "🟢" if "多" in recommendation["bias"] else "🔴" if "空" in recommendation["bias"] else "🟡"
            lines.append(f"- **工具建议**: {bias_emoji} {recommendation['bias']}")
            if recommendation.get("confidence"):
                lines.append(f"- **建议置信度**: {recommendation['confidence']}")
        
        # 风险因素
        risk_factors = recommendation.get("risk_factors", [])
        if risk_factors:
            lines.append(f"- **主要风险**: {', '.join(risk_factors[:2])}")
        
        return "\n".join(lines) if lines else "经济数据内容有限"

    def _format_technical_data_for_analysis(self, technical_data):
        """格式化技术数据用于分析 - 增强交易信号信息"""
        if not technical_data:
            return "无技术分析数据"
        
        lines = []
        
        data_type = technical_data.get("data_type")
        lines.append(f"- **数据类型**: {data_type}")
        
        if data_type == "trading_signals":
            # 交易信号格式 - 增强显示
            composite = technical_data.get("composite_signal", {})
            if composite.get("recommendation"):
                signal_emoji = "🟢" if "多" in composite["recommendation"] else "🔴" if "空" in composite["recommendation"] else "🟡"
                lines.append(f"- **综合信号**: {signal_emoji} {composite['recommendation']}")
                if composite.get("confidence"):
                    conf_level = "强" if composite['confidence'] > 70 else "弱" if composite['confidence'] < 30 else "中"
                    lines.append(f"- **信号强度**: {composite['confidence']}% ({conf_level})")
            
            # 多空信号对比
            bullish_count = composite.get("bullish_count", 0)
            bearish_count = composite.get("bearish_count", 0)
            lines.append(f"- **多空对比**: {bullish_count}个看涨 vs {bearish_count}个看跌")
            
            # 详细指标信号
            signals = technical_data.get("signals", {})
            indicator_lines = []
            
            if signals.get("rsi"):
                rsi_val = signals["rsi"].get("value")
                if rsi_val:
                    rsi_status = "超卖" if rsi_val < 30 else "超买" if rsi_val > 70 else "中性"
                    indicator_lines.append(f"RSI({rsi_val}-{rsi_status})")
            
            if signals.get("macd"):
                macd_signal = signals["macd"].get("signal", "")
                if macd_signal:
                    indicator_lines.append(f"MACD({macd_signal})")
            
            if signals.get("trend"):
                trend_strength = signals["trend"].get("strength", "")
                if trend_strength:
                    indicator_lines.append(f"趋势({trend_strength})")
            
            if indicator_lines:
                lines.append(f"- **关键指标**: {', '.join(indicator_lines)}")
                
        elif data_type == "technical_indicators":
            # 技术指标格式 - 增强显示
            indicators = technical_data.get("indicators", {})
            indicator_lines = []
            
            if indicators.get("RSI"):
                rsi_val = indicators["RSI"]
                rsi_status = "超卖" if rsi_val < 30 else "超买" if rsi_val > 70 else "中性"
                indicator_lines.append(f"RSI({rsi_val}-{rsi_status})")
            
            if indicators.get("MACD"):
                macd_val = indicators["MACD"]
                macd_signal = "看涨" if macd_val > 0 else "看跌"
                indicator_lines.append(f"MACD({macd_val}-{macd_signal})")
            
            if indicators.get("BB_Position"):
                bb_pos = indicators["BB_Position"]
                bb_status = "上轨" if bb_pos > 0.7 else "下轨" if bb_pos < 0.3 else "中轨"
                indicator_lines.append(f"布林带({bb_status})")
            
            if indicator_lines:
                lines.append(f"- **技术指标**: {', '.join(indicator_lines)}")
            
            # 价格摘要
            price_info = technical_data.get("price", {})
            if price_info.get("current"):
                change_emoji = "📈" if price_info.get("change_pct", 0) > 0 else "📉"
                lines.append(f"- **当前价格**: {price_info['current']} {change_emoji}")
        
        return "\n".join(lines) if lines else "技术数据内容有限"

    # 保留原有的数据提取方法（不需要修改）
    def _extract_market_data(self, market_data):
        """提取市场数据 - 适配data_fetcher的实际格式"""
        # 保持原有实现不变
        key_data = {}
        
        if not market_data or not market_data.get("success"):
            return key_data
        
        try:
            data_content = market_data.get("data", {})
            
            # 处理实时数据（单个字典）
            if isinstance(data_content, dict) and data_content:
                key_data["price"] = {
                    "exchange_rate": data_content.get("exchange_rate"),
                    "open": data_content.get("open"),
                    "high": data_content.get("high"),
                    "low": data_content.get("low"), 
                    "close": data_content.get("exchange_rate"),
                    "volume": data_content.get("volume"),
                    "change": data_content.get("change"),
                    "percent_change": data_content.get("percent_change")
                }
                key_data["currency_info"] = {
                    "from_currency": data_content.get("from_currency"),
                    "to_currency": data_content.get("to_currency"),
                    "pair": market_data.get("currency_pair")
                }
                key_data["metadata"] = {
                    "data_type": "real_time",
                    "success": market_data.get("success"),
                    "source": "data_fetcher"
                }
            
            # 处理历史/日内数据（列表格式）
            elif isinstance(data_content, list) and len(data_content) > 0:
                latest = data_content[-1]
                key_data["price"] = {
                    "open": latest.get("open"),
                    "high": latest.get("high"),
                    "low": latest.get("low"),
                    "close": latest.get("close"),
                    "volume": latest.get("volume"),
                    "datetime": latest.get("datetime")
                }
                key_data["summary"] = market_data.get("summary", {})
                key_data["metadata"] = {
                    "data_type": "historical",
                    "success": market_data.get("success"),
                    "source": "data_fetcher"
                }
            
        except Exception as e:
            logger.error(f"提取市场数据失败: {e}")
            key_data["error"] = f"数据提取错误: {str(e)}"
        
        return key_data

    def _extract_economic_data(self, economic_data):
        """提取经济数据 - 适配economic_calendar的实际复杂格式"""
        # 保持原有实现不变
        extracted = {}
        
        if not economic_data or not economic_data.get("success"):
            return extracted
        
        try:
            # 处理多货币对分析结果
            if economic_data.get("analysis_type") == "multi_currency":
                extracted["analysis_type"] = "multi_currency"
                extracted["currency_pairs"] = economic_data.get("currency_pairs_analyzed", [])
                extracted["summary"] = economic_data.get("summary", {})
                # 取第一个货币对的详细分析作为代表
                individual_analyses = economic_data.get("individual_analyses", {})
                if individual_analyses:
                    first_pair = list(individual_analyses.keys())[0]
                    representative_data = individual_analyses[first_pair]
                    if representative_data.get("success"):
                        extracted.update(self._extract_single_currency_economic_data(representative_data))
            else:
                # 单货币对分析
                extracted.update(self._extract_single_currency_economic_data(economic_data))
            
        except Exception as e:
            logger.error(f"提取经济数据失败: {e}")
            extracted["error"] = str(e)
        
        return extracted

    def _extract_single_currency_economic_data(self, economic_data):
        """提取单货币对经济数据"""
        # 保持原有实现不变
        extracted = {}
        
        try:
            # 提取市场情绪
            market_context = economic_data.get("market_context", {})
            extracted["sentiment"] = {
                "overall": market_context.get("overall_sentiment"),
                "score": market_context.get("sentiment_score"),
                "key_themes": market_context.get("key_market_themes", []),
                "volatility": market_context.get("volatility_outlook")
            }
            
            # 提取经济事件
            calendar_analysis = economic_data.get("economic_calendar_analysis", {})
            extracted["events"] = [
                {
                    "name": e.get("event_name"),
                    "date": e.get("event_date"),
                    "importance": e.get("importance_level"),
                    "actual": e.get("actual_value"),
                    "status": e.get("status")
                }
                for e in calendar_analysis.get("events", [])
            ]
            
            extracted["event_summary"] = {
                "total_events": calendar_analysis.get("total_events", 0),
                "high_impact_events": calendar_analysis.get("high_impact_events", 0),
                "period_covered": calendar_analysis.get("period_covered", "")
            }
            
            # 提取交易建议
            trading_rec = economic_data.get("trading_recommendation", {})
            extracted["recommendation"] = {
                "bias": trading_rec.get("overall_bias"),
                "confidence": trading_rec.get("confidence_level"),
                "risk_factors": trading_rec.get("key_risk_factors", []),
                "actions": trading_rec.get("recommended_actions", [])
            }
            
        except Exception as e:
            logger.error(f"提取单货币经济数据失败: {e}")
            extracted["error"] = str(e)
        
        return extracted

    def _extract_technical_data(self, technical_data):
        """提取技术分析数据 - 适配technical_analyzer的实际格式"""
        # 保持原有实现不变
        extracted = {}
        
        if not technical_data or not technical_data.get("success"):
            return extracted
        
        try:
            # 判断数据来源：calculate_indicators 还是 generate_signals
            data_type = self._detect_technical_data_type(technical_data)
            
            if data_type == "indicators":
                extracted["data_type"] = "technical_indicators"
                extracted["symbol"] = technical_data.get("symbol")
                extracted["record_count"] = technical_data.get("record_count", 0)
                
                # 提取价格摘要
                price_summary = technical_data.get("price_summary", {})
                extracted["price"] = {
                    "current": price_summary.get("current_price"),
                    "change": price_summary.get("price_change"),
                    "change_pct": price_summary.get("price_change_pct")
                }
                
                # 提取技术指标数据
                data_list = technical_data.get("data", [])
                if data_list:
                    latest_data = data_list[-1]
                    extracted["indicators"] = self._extract_indicators_from_data(latest_data)
                
                extracted["available_indicators"] = technical_data.get("indicators_calculated", [])
                
            elif data_type == "signals":
                extracted["data_type"] = "trading_signals"
                extracted["symbol"] = technical_data.get("symbol")
                extracted["timestamp"] = technical_data.get("timestamp")
                extracted["price"] = technical_data.get("price")
                
                # 提取各个技术信号
                extracted["signals"] = {
                    "rsi": technical_data.get("rsi", {}),
                    "macd": technical_data.get("macd", {}),
                    "bollinger_bands": technical_data.get("bollinger_bands", {}),
                    "stochastic": technical_data.get("stochastic", {}),
                    "moving_averages": technical_data.get("moving_averages", {}),
                    "trend": technical_data.get("trend", {}),
                    "volatility": technical_data.get("volatility", {})
                }
                
                # 提取综合信号
                composite_signal = technical_data.get("composite_signal", {})
                extracted["composite_signal"] = {
                    "recommendation": composite_signal.get("recommendation"),
                    "confidence": composite_signal.get("confidence"),
                    "bullish_count": composite_signal.get("bullish_signals"),
                    "bearish_count": composite_signal.get("bearish_signals")
                }
                
            extracted["metadata"] = {
                "success": technical_data.get("success", False),
                "data_type": data_type,
                "source": "technical_analyzer"
            }
            
        except Exception as e:
            logger.error(f"提取技术数据失败: {e}")
            extracted["error"] = str(e)
        
        return extracted

    def _detect_technical_data_type(self, data):
        """检测技术数据的类型"""
        if "composite_signal" in data:
            return "signals"
        elif "data" in data and "indicators_calculated" in data:
            return "indicators"
        else:
            return "unknown"

    def _extract_indicators_from_data(self, data_point):
        """从数据点中提取技术指标"""
        indicators = {}
        
        indicator_fields = [
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'Stoch_K', 'Stoch_D', 'BB_Upper', 'BB_Middle', 
            'BB_Lower', 'BB_Width', 'BB_Position', 'ATR'
        ]
        
        for i in [5, 10, 20, 50, 200]:
            indicator_fields.append(f'EMA_{i}')
        
        for field in indicator_fields:
            if field in data_point:
                value = data_point[field]
                if value is None or (isinstance(value, float) and np.isnan(value)):
                    indicators[field] = None
                else:
                    indicators[field] = value
        
        return indicators

    




    def _get_timestamp(self) -> str:
        """获取时间戳"""
        return datetime.now().isoformat()


    def react_reasoning(self, question: str, available_tools: list = None, context: str = None) -> Dict[str, Any]:
        """
        ReAct推理 - 分析问题并制定调查计划
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI客户端未初始化，请检查API密钥配置",
                "reasoning_plan": None
            }
        
        try:
            prompt = f"""
    作为外汇交易分析师，请分析以下问题并制定调查计划：

    问题: {question}
    可用工具: {available_tools or ['data_fetcher', 'technical_analyzer', 'economic_calendar']}
    上下文: {context or '无'}

    请分析：
    1. **确定目标货币对**：从问题中识别出主要的分析货币对（例如 EUR/USD, GBP/JPY）。如果没有明确指出，则尝试推断最相关的货币对。
    2. 这个问题需要哪些类型的数据？（经济数据、新闻、技术分析等）
    3. 应该按什么顺序收集这些数据？
    4. 哪些是关键因素需要重点关注？

    请以JSON格式返回推理计划：
    {{
        "reasoning": "思考过程描述",
        "target_currency_pair": "识别出的目标货币对，例如 EUR/USD 或 N/A",
        "need_economic_data": true/false,
        "need_technical_analysis": true/false,
        "need_market_data": true/false,
        "need_news_analysis": true/false,
        "investigation_steps": ["步骤1", "步骤2", "步骤3"],
        "key_factors": ["因素1", "因素2"],
        "expected_data_sources": ["source1", "source2"]
    }}
    """
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "您是专业的外汇市场分析师，擅长制定调查计划，请务必从问题中识别目标货币对。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            reasoning_plan = json.loads(response.choices[0].message.content)

            # 货币对格式处理
            pair = reasoning_plan.get("target_currency_pair")
            if pair and isinstance(pair, str) and pair.upper() != "N/A":
                # 简化处理：保持原始格式，让调用方处理
                reasoning_plan["target_currency_pair"] = pair.upper().replace(" ", "")
            
            return {
                "success": True,
                "reasoning_plan": reasoning_plan,
                "query": question,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"ReAct推理失败: {e}")
            return {
                "success": False,
                "error": f"推理计划生成失败: {str(e)}",
                "reasoning_plan": None
            }
        

    def evaluate_evidence(self, question: str, current_findings: Dict[str, Any], 
                        collected_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        中期推理 - 评估已收集证据并决定下一步
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI客户端未初始化",
                "evaluation": None
            }
        
        try:
            prompt = f"""
    基于已收集的证据，评估分析进展：

    原始问题: {question}
    当前推理计划: {json.dumps(current_findings, ensure_ascii=False, indent=2)}

    已收集数据:
    {json.dumps(collected_data or {}, ensure_ascii=False, indent=2)}

    请评估：
    1. 当前证据是否足够回答原问题？
    2. 还需要哪些额外信息？
    3. 发现了哪些关键线索？
    4. 建议的下一步行动是什么？

    请以JSON格式返回评估结果：
    {{
        "reasoning": "评估思考过程",
        "evidence_sufficient": true/false,
        "need_more_data": true/false,
        "missing_information": ["信息1", "信息2"],
        "key_insights": ["发现1", "发现2"],
        "next_steps": ["下一步1", "下一步2"],
        "confidence_level": "高/中/低"
    }}
    """
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "您是专业的数据分析师，擅长评估证据完整性。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "evaluation": evaluation,
                "question": question,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"证据评估失败: {e}")
            return {
                "success": False,
                "error": f"证据评估失败: {str(e)}",
                "evaluation": None
            }

    def react_final_analysis(self, question: str, reasoning_steps: Dict[str, Any],
                            all_collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ReAct最终分析 - 基于推理过程和数据生成最终答案
        """
        if not self.client:
            return {
                "success": False,
                "error": "AI客户端未初始化",
                "final_analysis": None
            }
        
        try:
            prompt = f"""
    基于完整的ReAct推理过程和数据收集，请给出最终分析：

    原始问题: {question}

    推理过程记录:
    {json.dumps(reasoning_steps, ensure_ascii=False, indent=2)}

    所有收集的数据:
    {json.dumps(all_collected_data, ensure_ascii=False, indent=2)}

    请进行综合推理分析：
    1. 总结整个调查过程
    2. 基于所有证据给出明确答案
    3. 提供数据支持的关键发现
    4. 给出专业结论和建议

    请以JSON格式返回最终分析：
    {{
        "reasoning_process_summary": "推理过程总结",
        "key_findings": ["发现1", "发现2"],
        "primary_causes": ["原因1", "原因2"],
        "supporting_evidence": {{
            "evidence1": "数据支持1",
            "evidence2": "数据支持2"
        }},
        "confidence_level": "高/中/低",
        "final_conclusion": "最终结论",
        "recommendations": ["建议1", "建议2"],
        "limitations": ["限制1", "限制2"]
    }}
    """
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "您是顶级外汇分析师，擅长基于推理过程和数据给出专业结论。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            final_analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "final_analysis": final_analysis,
                "reasoning_steps_used": len(reasoning_steps),
                "data_sources_used": list(all_collected_data.keys()),
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"最终分析失败: {e}")
            
            return {
                "success": False,
                "error": f"最终分析失败: {str(e)}",
                "final_analysis": None
            }
        
    def quick_analysis(self, data: Dict[str, Any], analysis_type: str = "general") -> Dict[str, Any]:
        """快速分析单个数据源"""
        if not self.client:
            return {"success": False, "error": "AI客户端未初始化"}
        
        try:
            prompt = f"请对以下{analysis_type}数据进行分析: {json.dumps(data, ensure_ascii=False)}"
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": "您是数据分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "type": analysis_type
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = "healthy" if self.client else "degraded"
        ai_status = "available" if self.client else "unavailable"
        
        return {
            "status": status,
            "service": "analyzer",
            "ai_capabilities": ai_status,
            "default_model": self.default_model,
            "openai_configured": bool(self.openai_api_key),
            "base_url_configured": bool(self.openai_base_url),
            "timestamp": self._get_timestamp()
        }
