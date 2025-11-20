"""
TwelveData adapter for real-time and historical financial data.

Provides access to:
- Real-time stock, forex, cryptocurrency prices
- Historical data with various intervals
- Technical indicators
- Market news and fundamentals
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

from .base import BaseDataAdapter
from .types import (
    Asset,
    AssetPrice,
    AssetSearchQuery,
    AssetSearchResult,
    AssetType,
    DataSource,
    Exchange,
    MarketInfo,
    NameInfo,
    PriceInfo,
)

logger = logging.getLogger(__name__)


class TwelveDataAdapter(BaseDataAdapter):
    """TwelveData adapter for financial market data."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize TwelveData adapter.
        
        Args:
            api_key: TwelveData API key (defaults to TWELVE_DATA_API_KEY env var)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        
        self.source = DataSource.TWELVE_DATA
        self.api_key = api_key or os.getenv("TWELVE_DATA_API_KEY")
        self.base_url = "https://api.twelvedata.com"
        
        if not self.api_key:
            logger.warning("TwelveData API key not provided")
        
        # Rate limiting
        self.requests_per_minute = 8  # Free tier limit
        self.last_request_time = None
        
        logger.info(f"TwelveData adapter initialized (API key: {'***' + self.api_key[-4:] if self.api_key else 'None'})")

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request to TwelveData with rate limiting.
        
        Args:
            endpoint: API endpoint
            params: API parameters
            
        Returns:
            JSON response or None if failed
        """
        if not self.api_key:
            logger.error("TwelveData API key not configured")
            return None
            
        # Rate limiting
        if self.last_request_time:
            time_since_last = (datetime.now() - self.last_request_time).total_seconds()
            if time_since_last < 60 / self.requests_per_minute:
                wait_time = (60 / self.requests_per_minute) - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                import time
                time.sleep(wait_time)
        
        try:
            request_params = {
                "apikey": self.api_key,
                **params
            }
            
            url = f"{self.base_url}/{endpoint}"
            self.last_request_time = datetime.now()
            response = requests.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if data.get("status") == "error":
                logger.error(f"TwelveData API error: {data.get('message', 'Unknown error')}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TwelveData request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"TwelveData API error: {e}")
            return None

    def get_capabilities(self) -> List[Dict]:
        """Get adapter capabilities.
        
        Returns:
            List of capability descriptions
        """
        return [
            {
                "asset_types": [
                    AssetType.STOCK,
                    AssetType.ETF,
                    AssetType.FOREX,
                    AssetType.CRYPTO,
                    AssetType.INDEX
                ],
                "exchanges": [
                    Exchange.NASDAQ,
                    Exchange.NYSE,
                    Exchange.AMEX,
                    Exchange.FOREX,
                    Exchange.CRYPTO
                ],
                "features": ["real_time", "historical", "search", "fundamentals"]
            }
        ]

    def get_supported_asset_types(self) -> List[AssetType]:
        """Get list of supported asset types.
        
        Returns:
            List of supported asset types
        """
        return [
            AssetType.STOCK,
            AssetType.ETF, 
            AssetType.FOREX,
            AssetType.CRYPTO,
            AssetType.INDEX
        ]

    def validate_ticker(self, ticker: str) -> bool:
        """Validate ticker format for TwelveData.
        
        Args:
            ticker: Ticker to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not ticker or ":" not in ticker:
            return False
            
        exchange, symbol = ticker.split(":", 1)
        
        # TwelveData uses different symbol formats
        valid_prefixes = ["NASDAQ", "NYSE", "AMEX", "FX", "CRYPTO"]
        return exchange in valid_prefixes

    def _convert_twelve_data_symbol(self, ticker: str) -> str:
        """Convert internal ticker format to TwelveData symbol format.
        
        Args:
            ticker: Internal ticker format (e.g., "NASDAQ:AAPL")
            
        Returns:
            TwelveData symbol format
        """
        if ":" not in ticker:
            return ticker
            
        exchange, symbol = ticker.split(":", 1)
        
        # Map exchanges to TwelveData formats
        if exchange == "FX":
            # Forex pairs: EUR/USD format
            if len(symbol) == 6:
                return f"{symbol[:3]}/{symbol[3:]}"
        elif exchange == "CRYPTO":
            # Cryptocurrencies: BTC/USD format
            return f"{symbol}/USD"
            
        return symbol

    def search_assets(self, query: AssetSearchQuery) -> List[AssetSearchResult]:
        """Search for assets using TwelveData.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of search results
        """
        if not query.query:
            return []
            
        results = []
        
        # TwelveData symbol search
        params = {
            "symbol": query.query,
            "outputsize": min(query.limit, 30)
        }
        
        data = self._make_request("symbol_search", params)
        if not data or "data" not in data:
            return []
            
        for item in data["data"]:
            try:
                symbol = item["symbol"]
                exchange = item.get("exchange", "").upper()
                
                # Map exchange to internal format
                if exchange in ["NASDAQ", "NYSE", "AMEX"]:
                    ticker = f"{exchange}:{symbol}"
                    asset_type = AssetType.STOCK
                elif "forex" in exchange.lower():
                    ticker = f"FX:{symbol.replace('/', '')}"
                    asset_type = AssetType.FOREX
                elif "crypto" in exchange.lower():
                    ticker = f"CRYPTO:{symbol.split('/')[0]}"
                    asset_type = AssetType.CRYPTO
                else:
                    continue
                    
                result = AssetSearchResult(
                    ticker=ticker,
                    asset_type=asset_type,
                    names=[item.get("instrument_name", symbol)],
                    exchange=Exchange(exchange) if exchange else Exchange.NASDAQ,
                    country=item.get("country", "US"),
                    description=item.get("instrument_name", ""),
                    relevance_score=float(item.get("score", 0.5))
                )
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Failed to parse search result: {e}")
                continue
                
        logger.info(f"TwelveData search returned {len(results)} results for: {query.query}")
        return results

    def get_asset_info(self, ticker: str) -> Optional[Asset]:
        """Get asset information from TwelveData.
        
        Args:
            ticker: Asset ticker
            
        Returns:
            Asset information or None if not found
        """
        if not self.validate_ticker(ticker):
            return None
            
        symbol = self._convert_twelve_data_symbol(ticker)
        
        # Get profile information
        params = {
            "symbol": symbol
        }
        
        data = self._make_request("profile", params)
        if not data:
            return None
            
        # Determine asset type and exchange
        if ticker.startswith("FX:"):
            asset_type = AssetType.FOREX
            exchange = Exchange.FOREX
            country = "Global"
            currency = ticker.split(":")[1][3:] if len(ticker.split(":")[1]) == 6 else "USD"
        elif ticker.startswith("CRYPTO:"):
            asset_type = AssetType.CRYPTO
            exchange = Exchange.CRYPTO
            country = "Global"
            currency = "USD"
        else:
            asset_type = AssetType.STOCK
            exchange = Exchange(ticker.split(":")[0])
            country = data.get("country", "US")
            currency = data.get("currency", "USD")
            
        return Asset(
            ticker=ticker,
            asset_type=asset_type,
            names=NameInfo(
                names=[data.get("name", symbol)],
                short_name=data.get("symbol", symbol),
                long_name=data.get("name", symbol)
            ),
            market_info=MarketInfo(
                exchange=exchange,
                country=country,
                currency=currency,
                timezone=data.get("timezone", "UTC")
            )
        )

    def get_real_time_price(self, ticker: str) -> Optional[AssetPrice]:
        """Get real-time price from TwelveData.
        
        Args:
            ticker: Asset ticker
            
        Returns:
            Current price data or None if not available
        """
        if not self.validate_ticker(ticker):
            return None
            
        symbol = self._convert_twelve_data_symbol(ticker)
        
        params = {
            "symbol": symbol,
            "interval": "1min"
        }
        
        data = self._make_request("price", params)
        if not data or "price" not in data:
            return None
            
        # Get additional quote data for change information
        quote_data = self._make_request("quote", {"symbol": symbol})
        
        price = float(data["price"])
        change = 0
        change_percent = 0
        
        if quote_data:
            change = float(quote_data.get("change", 0))
            change_percent = float(quote_data.get("percent_change", "0").rstrip("%"))
            
        return AssetPrice(
            ticker=ticker,
            price=price,
            currency="USD",  # TwelveData returns USD prices
            timestamp=datetime.now(),
            change=change,
            change_percent=change_percent,
            volume=0,  # Volume not available in price endpoint
            price_info=PriceInfo(
                open=price - change,  # Estimate open price
                high=price,
                low=price,
                close=price
            )
        )

    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, Optional[AssetPrice]]:
        """Get real-time prices for multiple assets.
        
        Args:
            tickers: List of asset tickers
            
        Returns:
            Dictionary mapping tickers to price data
        """
        results = {}
        valid_tickers = [t for t in tickers if self.validate_ticker(t)]
        
        if not valid_tickers:
            return results
            
        # Convert tickers to TwelveData symbols
        symbols = [self._convert_twelve_data_symbol(t) for t in valid_tickers]
        symbol_str = ",".join(symbols)
        
        params = {
            "symbol": symbol_str,
            "interval": "1min"
        }
        
        data = self._make_request("price", params)
        if not data:
            # Fallback to individual requests
            for ticker in valid_tickers:
                price = self.get_real_time_price(ticker)
                results[ticker] = price
            return results
            
        # Parse batch response
        for ticker, symbol in zip(valid_tickers, symbols):
            if symbol in data:
                price_data = data[symbol]
                if "price" in price_data:
                    results[ticker] = AssetPrice(
                        ticker=ticker,
                        price=float(price_data["price"]),
                        currency="USD",
                        timestamp=datetime.now(),
                        change=0,
                        change_percent=0,
                        volume=0,
                        price_info=PriceInfo(
                            open=float(price_data["price"]),
                            high=float(price_data["price"]),
                            low=float(price_data["price"]),
                            close=float(price_data["price"])
                        )
                    )
                else:
                    results[ticker] = None
            else:
                results[ticker] = None
                
        return results

    def get_historical_prices(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> List[AssetPrice]:
        """Get historical price data from TwelveData.
        
        Args:
            ticker: Asset ticker
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval ("1d", "1h", "5min", etc.)
            
        Returns:
            List of historical price data
        """
        if not self.validate_ticker(ticker):
            return []
            
        symbol = self._convert_twelve_data_symbol(ticker)
        
        # Calculate time range
        days_diff = (end_date - start_date).days
        
        # Determine outputsize based on time range
        if days_diff <= 30:
            outputsize = 30
        elif days_diff <= 100:
            outputsize = 100
        else:
            outputsize = 5000  # Maximum for free tier
            
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        data = self._make_request("time_series", params)
        if not data or "values" not in data:
            return []
            
        prices = []
        for value in data["values"]:
            try:
                price_date = datetime.strptime(value["datetime"], "%Y-%m-%d %H:%M:%S")
                
                asset_price = AssetPrice(
                    ticker=ticker,
                    price=float(value.get("close", 0)),
                    currency="USD",
                    timestamp=price_date,
                    change=float(value.get("close", 0)) - float(value.get("open", 0)),
                    change_percent=((float(value.get("close", 0)) - float(value.get("open", 0))) / float(value.get("open", 1))) * 100,
                    volume=int(value.get("volume", 0)),
                    price_info=PriceInfo(
                        open=float(value.get("open", 0)),
                        high=float(value.get("high", 0)),
                        low=float(value.get("low", 0)),
                        close=float(value.get("close", 0))
                    )
                )
                prices.append(asset_price)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse historical data: {e}")
                continue
                
        # Sort by date
        prices.sort(key=lambda x: x.timestamp)
        
        logger.info(f"Retrieved {len(prices)} historical prices for {ticker}")
        return prices