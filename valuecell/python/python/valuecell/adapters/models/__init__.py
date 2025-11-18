"""
Model Adapters - Factory and providers for creating AI model instances

This module provides a unified interface for creating and managing different AI model providers
through the ModelFactory class and various provider implementations.

Main Components:
- ModelFactory: Factory class for creating model instances
- ModelProvider: Abstract base class for provider implementations
- Provider implementations: OpenRouterProvider, GoogleProvider, AzureProvider, etc.
- Data providers: AlphaVantageProvider, TwelveDataProvider for financial data

Usage:
    >>> from valuecell.adapters.models import create_model, create_model_for_agent
    >>>
    >>> # Create a model with default provider
    >>> model = create_model()
    >>>
    >>> # Create a model for a specific agent
    >>> model = create_model_for_agent("research_agent")
    >>>
    >>> # Create financial data clients
    >>> alpha_client = create_model(provider="alphavantage")
    >>> twelve_client = create_model(provider="twelvedata")
"""

from valuecell.adapters.models.factory import (
    AlphaVantageProvider,
    AzureProvider,
    GoogleProvider,
    ModelFactory,
    ModelProvider,
    OpenRouterProvider,
    SiliconFlowProvider,
    TwelveDataProvider,
    create_model,
    create_model_for_agent,
    get_model_factory,
)

# 导出数据客户端类，方便直接使用
from valuecell.adapters.models.factory import AlphaVantageClient, TwelveDataClient

__all__ = [
    # Factory and base classes
    "ModelFactory",
    "ModelProvider",
    "get_model_factory",
    
    # LLM Provider implementations
    "OpenRouterProvider",
    "GoogleProvider",
    "AzureProvider",
    "SiliconFlowProvider",
    
    # Financial Data Provider implementations - 新增
    "AlphaVantageProvider",
    "TwelveDataProvider",
    
    # Data Client classes - 新增
    "AlphaVantageClient",
    "TwelveDataClient",
    
    # Convenience functions
    "create_model",
    "create_model_for_agent",
]