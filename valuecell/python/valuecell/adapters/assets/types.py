"""
Type definitions for asset data adapters.

This module defines the core data structures and types used throughout
the asset data adapter system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class Interval(str, Enum):
    """Data interval enumeration."""
    
    ONE_MINUTE = "1min"
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"


class AssetType(str, Enum):
    """Enumeration of supported asset types."""

    STOCK = "stock"
    CRYPTO = "crypto"
    ETF = "etf"
    FOREX = "forex"
    INDEX = "index"
    # BOND = "bond"
    # COMMODITY = "commodity"
    # MUTUAL_FUND = "mutual_fund"
    # OPTION = "option"
    # FUTURE = "future"


class Exchange(str, Enum):
    """Enumeration of supported exchanges."""

    NASDAQ = "NASDAQ"  # NASDAQ Market in the US
    NYSE = "NYSE"  # NYSE Market in the US
    AMEX = "AMEX"  # AMEX Market in the US
    SSE = "SSE"  # Shanghai Stock Exchange
    SZSE = "SZSE"  # Shenzhen Stock Exchange
    BSE = "BSE"  # Beijing Stock Exchange
    HKEX = "HKEX"  # Hong Kong Stock Exchange
    CRYPTO = "CRYPTO"  # Crypto Market
    FOREX = "FOREX"  # Forex Market


class MarketStatus(str, Enum):
    """Market status enumeration."""

    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"
    HALTED = "halted"
    UNKNOWN = "unknown"


class DataSource(str, Enum):
    """Supported data source providers."""

    YFINANCE = "yfinance"
    AKSHARE = "akshare"
    ALPHA_VANTAGE = "alpha_vantage"
    TWELVE_DATA = "twelve_data"


@dataclass
class LocalizedName:
    """Localized name information."""
    
    language: str = "en"
    name: str = ""
    description: str = ""


@dataclass
class NameInfo:
    """Asset naming information."""
    
    names: List[str] = field(default_factory=list)
    short_name: str = ""
    long_name: str = ""
    description: str = ""
    localized_names: List[LocalizedName] = field(default_factory=list)


@dataclass
class MarketInfo:
    """Market and exchange information."""
    
    exchange: Exchange
    country: str = ""
    currency: str = "USD"
    timezone: str = "UTC"
    market_status: MarketStatus = MarketStatus.UNKNOWN


@dataclass
class PriceInfo:
    """Detailed price information."""
    
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    previous_close: float = 0.0
    volume: int = 0
    market_cap: Optional[float] = None


@dataclass
class Asset:
    """Complete asset information."""
    
    ticker: str
    asset_type: AssetType
    names: NameInfo
    market_info: MarketInfo
    metadata: Dict = field(default_factory=dict)


@dataclass
class AssetPrice:
    """Asset price data at a specific timestamp."""
    
    ticker: str
    price: float
    currency: str
    timestamp: datetime
    change: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    price_info: Optional[PriceInfo] = None
    
    def __post_init__(self):
        """Initialize price_info if not provided."""
        if self.price_info is None:
            self.price_info = PriceInfo(
                open=self.price,
                high=self.price,
                low=self.price,
                close=self.price,
                previous_close=self.price - self.change,
                volume=self.volume
            )


@dataclass
class AssetSearchQuery:
    """Asset search query parameters."""
    
    query: str
    asset_types: List[AssetType] = field(default_factory=list)
    exchanges: List[Exchange] = field(default_factory=list)
    limit: int = 20
    offset: int = 0


@dataclass
class AssetSearchResult:
    """Asset search result."""
    
    ticker: str
    asset_type: AssetType
    names: List[str]
    exchange: Exchange
    country: str = ""
    description: str = ""
    relevance_score: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class WatchlistItem:
    """Watchlist item with user notes."""
    
    ticker: str
    added_at: datetime = field(default_factory=datetime.now)
    notes: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class Watchlist:
    """User watchlist for tracking assets."""
    
    user_id: str
    name: str
    description: str = ""
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    items: List[WatchlistItem] = field(default_factory=list)
    
    def add_asset(self, ticker: str, notes: str = "") -> bool:
        """Add an asset to the watchlist."""
        # Check if already exists
        for item in self.items:
            if item.ticker == ticker:
                return False
        
        self.items.append(WatchlistItem(ticker=ticker, notes=notes))
        self.updated_at = datetime.now()
        return True
    
    def remove_asset(self, ticker: str) -> bool:
        """Remove an asset from the watchlist."""
        for i, item in enumerate(self.items):
            if item.ticker == ticker:
                self.items.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_tickers(self) -> List[str]:
        """Get list of tickers in watchlist."""
        return [item.ticker for item in self.items]
    
    def find_item(self, ticker: str) -> Optional[WatchlistItem]:
        """Find watchlist item by ticker."""
        for item in self.items:
            if item.ticker == ticker:
                return item
        return None