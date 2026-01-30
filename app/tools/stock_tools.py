"""
Stock data fetching tools using yfinance.
"""

import yfinance as yf
from typing import Optional
from langchain_core.tools import tool


@tool
def fetch_price(ticker: str) -> dict:
    """
    Fetch the current price and daily change for a stock ticker.
    
    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL', 'TSLA', 'MSFT')
    
    Returns:
        Dictionary with current price, previous close, change, and percent change
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)
        
        if current_price and previous_close:
            change = current_price - previous_close
            percent_change = (change / previous_close) * 100
        else:
            change = 0
            percent_change = 0
        
        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "change": round(change, 2),
            "percent_change": round(percent_change, 2),
            "currency": info.get('currency', 'USD'),
            "market_state": info.get('marketState', 'UNKNOWN'),
            "success": True
        }
    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "error": str(e),
            "success": False
        }


@tool
def fetch_multiple_prices(tickers: list[str]) -> list[dict]:
    """
    Fetch prices for multiple stock tickers at once.
    
    Args:
        tickers: List of stock ticker symbols
    
    Returns:
        List of price data dictionaries for each ticker
    """
    results = []
    for ticker in tickers:
        result = fetch_price.invoke({"ticker": ticker})
        results.append(result)
    return results


@tool
def get_stock_info(ticker: str) -> dict:
    """
    Get detailed information about a stock.
    
    Args:
        ticker: The stock ticker symbol
    
    Returns:
        Dictionary with company name, sector, market cap, and other details
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        return {
            "ticker": ticker.upper(),
            "name": info.get('longName', info.get('shortName', 'Unknown')),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "dividend_yield": info.get('dividendYield'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
            "avg_volume": info.get('averageVolume'),
            "description": info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else '',
            "success": True
        }
    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "error": str(e),
            "success": False
        }


def get_price_sync(ticker: str) -> dict:
    """
    Synchronous version of fetch_price for internal use.
    
    Args:
        ticker: The stock ticker symbol
    
    Returns:
        Price data dictionary
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)
        
        if current_price and previous_close:
            change = current_price - previous_close
            percent_change = (change / previous_close) * 100
        else:
            change = 0
            percent_change = 0
        
        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2) if current_price else None,
            "previous_close": round(previous_close, 2) if previous_close else None,
            "change": round(change, 2),
            "percent_change": round(percent_change, 2),
            "success": True
        }
    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "error": str(e),
            "success": False
        }
