"""
AlphaVantage data adapter for financial market data.

Provides access to:
- Real-time and historical stock prices
- Forex rates
- Cryptocurrency data
- Economic indicators
- Technical indicators
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


class AlphaVantageAdapter(BaseDataAdapter):
    """AlphaVantage data adapter for financial market data."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize AlphaVantage adapter.
        
        Args:
            api_key: AlphaVantage API key (defaults to ALPHA_VANTAGE_API_KEY env var)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        
        self.source = DataSource.ALPHA_VANTAGE
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        
        if not self.api_key:
            logger.warning("AlphaVantage API key not provided")
        
        # Rate limiting
        self.requests_per_minute = 5  # Free tier limit
        self.last_request_time = None
        
        logger.info(f"AlphaVantage adapter initialized (API key: {'***' + self.api_key[-4:] if self.api_key else 'None'})")

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request to AlphaVantage with rate limiting.
        
        Args:
            params: API parameters
            
        Returns:
            JSON response or None if failed
        """
        if not self.api_key:
            logger.error("AlphaVantage API key not configured")
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
            
            self.last_request_time = datetime.now()
            response = requests.get(self.base_url, params=request_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.error(f"AlphaVantage API error: {data['Error Message']}")
                return None
            if "Note" in data:
                logger.warning(f"AlphaVantage API note: {data['Note']}")
            if "Information" in data:
                logger.info(f"AlphaVantage API info: {data['Information']}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AlphaVantage request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"AlphaVantage API error: {e}")
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
                "features": ["real_time", "historical", "search"]
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
        """Validate ticker format for AlphaVantage.
        
        Args:
            ticker: Ticker to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not ticker or ":" not in ticker:
            return False
            
        exchange, symbol = ticker.split(":", 1)
        
        # AlphaVantage uses different prefixes
        valid_prefixes = ["NASDAQ", "NYSE", "AMEX", "FX", "CRYPTO", "INDEX"]
        return exchange in valid_prefixes

    def _convert_alpha_vantage_ticker(self, ticker: str) -> str:
        """Convert internal ticker format to AlphaVantage format.
        
        Args:
            ticker: Internal ticker format (e.g., "NASDAQ:AAPL")
            
        Returns:
            AlphaVantage symbol format
        """
        if ":" not in ticker:
            return ticker
            
        exchange, symbol = ticker.split(":", 1)
        
        # Map exchanges to AlphaVantage formats
        exchange_map = {
            "NASDAQ": "",
            "NYSE": "", 
            "AMEX": "",
            "FX": "Forex",  # Forex pairs
            "CRYPTO": "Crypto",  # Cryptocurrencies
            "INDEX": "Index"  # Indices
        }
        
        prefix = exchange_map.get(exchange, "")
        if prefix:
            return f"{prefix}:{symbol}"
        else:
            return symbol

    def search_assets(self, query: AssetSearchQuery) -> List[AssetSearchResult]:
        """Search for assets using AlphaVantage.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of search results
        """
        if not query.query:
            return []
            
        results = []
        
        # AlphaVantage doesn't have a direct search API, so we implement basic matching
        # For now, return common forex pairs for forex-related queries
        forex_keywords = ["forex", "fx", "currency", "eur", "usd", "jpy", "gbp", "aud", "cad", "chf", "nzd"]
        
        if any(keyword in query.query.lower() for keyword in forex_keywords):
            common_forex_pairs = [
                ("FX:EURUSD", "EUR/USD", "Euro/US Dollar"),
                ("FX:GBPUSD", "GBP/USD", "British Pound/US Dollar"), 
                ("FX:USDJPY", "USD/JPY", "US Dollar/Japanese Yen"),
                ("FX:USDCHF", "USD/CHF", "US Dollar/Swiss Franc"),
                ("FX:AUDUSD", "AUD/USD", "Australian Dollar/US Dollar"),
                ("FX:USDCAD", "USD/CAD", "US Dollar/Canadian Dollar"),
                ("FX:NZDUSD", "NZD/USD", "New Zealand Dollar/US Dollar"),
            ]
            
            for ticker, name, description in common_forex_pairs:
                result = AssetSearchResult(
                    ticker=ticker,
                    asset_type=AssetType.FOREX,
                    names=[name],
                    exchange=Exchange.FOREX,
                    country="Global",
                    description=description,
                    relevance_score=0.8
                )
                results.append(result)
                
        logger.info(f"AlphaVantage search returned {len(results)} results for: {query.query}")
        return results

    def get_asset_info(self, ticker: str) -> Optional[Asset]:
        """Get asset information from AlphaVantage.
        
        Args:
            ticker: Asset ticker
            
        Returns:
            Asset information or None if not found
        """
        if not self.validate_ticker(ticker):
            return None
            
        # For forex pairs, create basic asset info
        if ticker.startswith("FX:"):
            _, pair = ticker.split(":", 1)
            base_currency = pair[:3]
            quote_currency = pair[3:]
            
            return Asset(
                ticker=ticker,
                asset_type=AssetType.FOREX,
                names=NameInfo(
                    names=[f"{base_currency}/{quote_currency}"],
                    short_name=f"{base_currency}/{quote_currency}",
                    long_name=f"{base_currency} to {quote_currency} Exchange Rate"
                ),
                market_info=MarketInfo(
                    exchange=Exchange.FOREX,
                    country="Global",
                    currency=quote_currency,
                    timezone="UTC"
                )
            )
            
        # For stocks, try to get overview data
        elif ticker.startswith(("NASDAQ:", "NYSE:", "AMEX:")):
            symbol = self._convert_alpha_vantage_ticker(ticker)
            
            params = {
                "function": "OVERVIEW",
                "symbol": symbol
            }
            
            data = self._make_request(params)
            if not data:
                return None
                
            return Asset(
                ticker=ticker,
                asset_type=AssetType.STOCK,
                names=NameInfo(
                    names=[data.get("Name", symbol)],
                    short_name=data.get("Symbol", symbol),
                    long_name=data.get("Name", symbol)
                ),
                market_info=MarketInfo(
                    exchange=Exchange(ticker.split(":")[0]),
                    country=data.get("Country", "US"),
                    currency=data.get("Currency", "USD"),
                    timezone=data.get("Timezone", "US/Eastern")
                )
            )
            
        return None

    def get_real_time_price(self, ticker: str) -> Optional[AssetPrice]:
        """Get real-time price from AlphaVantage.
        
        Args:
            ticker: Asset ticker
            
        Returns:
            Current price data or None if not available
        """
        if not self.validate_ticker(ticker):
            return None
            
        # Handle forex pairs
        if ticker.startswith("FX:"):
            _, pair = ticker.split(":", 1)
            from_currency = pair[:3]
            to_currency = pair[3:]
            
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_currency,
                "to_currency": to_currency
            }
            
            data = self._make_request(params)
            if not data or "Realtime Currency Exchange Rate" not in data:
                return None
                
            rate_data = data["Realtime Currency Exchange Rate"]
            
            return AssetPrice(
                ticker=ticker,
                price=float(rate_data.get("5. Exchange Rate", 0)),
                currency=to_currency,
                timestamp=datetime.now(),
                change=0,  # AlphaVantage doesn't provide change for forex
                change_percent=0,
                volume=0,
                price_info=PriceInfo(
                    open=float(rate_data.get("5. Exchange Rate", 0)),
                    high=float(rate_data.get("5. Exchange Rate", 0)),
                    low=float(rate_data.get("5. Exchange Rate", 0)),
                    close=float(rate_data.get("5. Exchange Rate", 0))
                )
            )
            
        # Handle stocks
        elif ticker.startswith(("NASDAQ:", "NYSE:", "AMEX:")):
            symbol = self._convert_alpha_vantage_ticker(ticker)
            
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol
            }
            
            data = self._make_request(params)
            if not data or "Global Quote" not in data:
                return None
                
            quote_data = data["Global Quote"]
            
            return AssetPrice(
                ticker=ticker,
                price=float(quote_data.get("05. price", 0)),
                currency="USD",
                timestamp=datetime.now(),
                change=float(quote_data.get("09. change", 0)),
                change_percent=float(quote_data.get("10. change percent", "0").rstrip("%")),
                volume=int(quote_data.get("06. volume", 0)),
                price_info=PriceInfo(
                    open=float(quote_data.get("02. open", 0)),
                    high=float(quote_data.get("03. high", 0)),
                    low=float(quote_data.get("04. low", 0)),
                    close=float(quote_data.get("05. price", 0))
                )
            )
            
        return None

    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, Optional[AssetPrice]]:
        """Get real-time prices for multiple assets.
        
        Args:
            tickers: List of asset tickers
            
        Returns:
            Dictionary mapping tickers to price data
        """
        results = {}
        
        # AlphaVantage has strict rate limits, so we do sequential requests
        for ticker in tickers:
            try:
                price = self.get_real_time_price(ticker)
                results[ticker] = price
                
                # Small delay to respect rate limits
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Failed to get price for {ticker}: {e}")
                results[ticker] = None
                
        return results

    def get_historical_prices(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> List[AssetPrice]:
        """Get historical price data from AlphaVantage.
        
        Args:
            ticker: Asset ticker
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval ("1d", "1h", etc.)
            
        Returns:
            List of historical price data
        """
        if not self.validate_ticker(ticker):
            return []
            
        # Map interval to AlphaVantage function
        interval_map = {
            "1d": "TIME_SERIES_DAILY",
            "1h": "TIME_SERIES_INTRADAY",
            "5min": "TIME_SERIES_INTRADAY",
            "15min": "TIME_SERIES_INTRADAY",
            "30min": "TIME_SERIES_INTRADAY",
            "60min": "TIME_SERIES_INTRADAY"
        }
        
        function = interval_map.get(interval, "TIME_SERIES_DAILY")
        
        params = {
            "function": function,
            "symbol": self._convert_alpha_vantage_ticker(ticker),
            "outputsize": "full" if (end_date - start_date).days > 100 else "compact"
        }
        
        if function == "TIME_SERIES_INTRADAY":
            params["interval"] = interval
            
        data = self._make_request(params)
        if not data:
            return []
            
        # Parse time series data
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break
                
        if not time_series_key:
            return []
            
        prices = []
        for date_str, price_data in data[time_series_key].items():
            try:
                # Parse date string (format depends on interval)
                if " " in date_str:
                    price_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    price_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                # Filter by date range
                if start_date <= price_date <= end_date:
                    asset_price = AssetPrice(
                        ticker=ticker,
                        price=float(price_data.get("4. close", 0)),
                        currency="USD",
                        timestamp=price_date,
                        change=0,  # Calculate if needed
                        change_percent=0,
                        volume=int(price_data.get("5. volume", 0)),
                        price_info=PriceInfo(
                            open=float(price_data.get("1. open", 0)),
                            high=float(price_data.get("2. high", 0)),
                            low=float(price_data.get("3. low", 0)),
                            close=float(price_data.get("4. close", 0))
                        )
                    )
                    prices.append(asset_price)
                    
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse historical data for {date_str}: {e}")
                continue
                
        # Sort by date
        prices.sort(key=lambda x: x.timestamp)
        
        logger.info(f"Retrieved {len(prices)} historical prices for {ticker}")
        return prices