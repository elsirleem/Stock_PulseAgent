"""
Portfolio management tools for the LangGraph agent.
"""

from langchain_core.tools import tool
from app.database import get_db
from app.tools.stock_tools import get_price_sync


@tool
def update_portfolio(user_phone: str, ticker: str, shares: float, purchase_price: float) -> dict:
    """
    Add or update a stock position in the user's portfolio.
    
    Args:
        user_phone: User's WhatsApp phone number
        ticker: Stock ticker symbol (e.g., 'AAPL')
        shares: Number of shares purchased
        purchase_price: Price per share at purchase
    
    Returns:
        Confirmation of the portfolio update
    """
    db = get_db()
    success = db.add_stock_to_portfolio(user_phone, ticker, shares, purchase_price)
    
    if success:
        return {
            "success": True,
            "message": f"Added {shares} shares of {ticker.upper()} at ${purchase_price:.2f} to your portfolio.",
            "ticker": ticker.upper(),
            "shares": shares,
            "purchase_price": purchase_price
        }
    else:
        return {
            "success": False,
            "message": f"Failed to add {ticker.upper()} to portfolio."
        }


@tool
def remove_from_portfolio(user_phone: str, ticker: str) -> dict:
    """
    Remove a stock from the user's portfolio.
    
    Args:
        user_phone: User's WhatsApp phone number
        ticker: Stock ticker symbol to remove
    
    Returns:
        Confirmation of removal
    """
    db = get_db()
    success = db.remove_stock_from_portfolio(user_phone, ticker)
    
    if success:
        return {
            "success": True,
            "message": f"Removed {ticker.upper()} from your portfolio."
        }
    else:
        return {
            "success": False,
            "message": f"{ticker.upper()} was not found in your portfolio."
        }


@tool
def get_portfolio(user_phone: str) -> dict:
    """
    Get all stocks in the user's portfolio.
    
    Args:
        user_phone: User's WhatsApp phone number
    
    Returns:
        List of portfolio holdings
    """
    db = get_db()
    holdings = db.get_user_portfolio(user_phone)
    
    if not holdings:
        return {
            "success": True,
            "holdings": [],
            "message": "Your portfolio is empty."
        }
    
    return {
        "success": True,
        "holdings": holdings,
        "count": len(holdings)
    }


@tool
def calculate_portfolio_stats(user_phone: str) -> dict:
    """
    Calculate comprehensive statistics for the user's portfolio including
    current values, gains/losses, and total portfolio value.
    
    Args:
        user_phone: User's WhatsApp phone number
    
    Returns:
        Portfolio statistics with current values and performance metrics
    """
    db = get_db()
    holdings = db.get_user_portfolio(user_phone)
    
    if not holdings:
        return {
            "success": True,
            "message": "Your portfolio is empty.",
            "total_value": 0,
            "total_cost": 0,
            "total_gain_loss": 0,
            "total_percent_change": 0,
            "holdings": []
        }
    
    detailed_holdings = []
    total_current_value = 0
    total_cost_basis = 0
    
    for holding in holdings:
        ticker = holding["ticker"]
        shares = holding["shares"]
        purchase_price = holding["purchase_price"]
        
        # Get current price
        price_data = get_price_sync(ticker)
        
        if price_data.get("success") and price_data.get("current_price"):
            current_price = price_data["current_price"]
            daily_change_pct = price_data.get("percent_change", 0)
        else:
            current_price = purchase_price  # Fallback to purchase price
            daily_change_pct = 0
        
        # Calculate values
        current_value = shares * current_price
        cost_basis = shares * purchase_price
        gain_loss = current_value - cost_basis
        percent_change = ((current_price - purchase_price) / purchase_price * 100) if purchase_price > 0 else 0
        
        total_current_value += current_value
        total_cost_basis += cost_basis
        
        detailed_holdings.append({
            "ticker": ticker,
            "shares": shares,
            "purchase_price": round(purchase_price, 2),
            "current_price": round(current_price, 2),
            "current_value": round(current_value, 2),
            "cost_basis": round(cost_basis, 2),
            "gain_loss": round(gain_loss, 2),
            "percent_change": round(percent_change, 2),
            "daily_change_pct": round(daily_change_pct, 2)
        })
    
    total_gain_loss = total_current_value - total_cost_basis
    total_percent_change = ((total_current_value - total_cost_basis) / total_cost_basis * 100) if total_cost_basis > 0 else 0
    
    return {
        "success": True,
        "total_value": round(total_current_value, 2),
        "total_cost": round(total_cost_basis, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "total_percent_change": round(total_percent_change, 2),
        "holdings": detailed_holdings
    }


@tool
def add_to_watchlist(user_phone: str, ticker: str) -> dict:
    """
    Add a stock to the user's watchlist.
    
    Args:
        user_phone: User's WhatsApp phone number
        ticker: Stock ticker symbol to watch
    
    Returns:
        Confirmation of addition
    """
    db = get_db()
    success = db.add_to_watchlist(user_phone, ticker)
    
    if success:
        return {
            "success": True,
            "message": f"Added {ticker.upper()} to your watchlist."
        }
    else:
        return {
            "success": False,
            "message": f"{ticker.upper()} is already in your watchlist."
        }


@tool
def remove_from_watchlist(user_phone: str, ticker: str) -> dict:
    """
    Remove a stock from the user's watchlist.
    
    Args:
        user_phone: User's WhatsApp phone number
        ticker: Stock ticker symbol to remove
    
    Returns:
        Confirmation of removal
    """
    db = get_db()
    success = db.remove_from_watchlist(user_phone, ticker)
    
    if success:
        return {
            "success": True,
            "message": f"Removed {ticker.upper()} from your watchlist."
        }
    else:
        return {
            "success": False,
            "message": f"{ticker.upper()} was not found in your watchlist."
        }


@tool
def get_watchlist(user_phone: str) -> dict:
    """
    Get all stocks in the user's watchlist with current prices.
    
    Args:
        user_phone: User's WhatsApp phone number
    
    Returns:
        List of watched stocks with current prices
    """
    db = get_db()
    tickers = db.get_watchlist(user_phone)
    
    if not tickers:
        return {
            "success": True,
            "watchlist": [],
            "message": "Your watchlist is empty."
        }
    
    watchlist_with_prices = []
    for ticker in tickers:
        price_data = get_price_sync(ticker)
        watchlist_with_prices.append({
            "ticker": ticker,
            "current_price": price_data.get("current_price"),
            "percent_change": price_data.get("percent_change"),
            "success": price_data.get("success", False)
        })
    
    return {
        "success": True,
        "watchlist": watchlist_with_prices,
        "count": len(tickers)
    }
