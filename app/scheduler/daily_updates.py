"""
APScheduler implementation for daily portfolio updates.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from twilio.rest import Client

from app.config import get_settings
from app.database import get_db
from app.tools.stock_tools import get_price_sync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: AsyncIOScheduler = None


def format_portfolio_update(user_phone: str) -> str:
    """
    Generate a formatted portfolio update message for a user.
    
    Args:
        user_phone: User's phone number
    
    Returns:
        Formatted update message string
    """
    db = get_db()
    holdings = db.get_user_portfolio(user_phone)
    watchlist = db.get_watchlist(user_phone)
    
    if not holdings and not watchlist:
        return None  # No update needed
    
    lines = []
    lines.append("🌅 *Good Morning! Here's your StockPulse Update*")
    lines.append(f"📅 {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")
    
    # Portfolio section
    if holdings:
        lines.append("📊 *Your Portfolio*")
        lines.append("─" * 20)
        
        total_value = 0
        total_cost = 0
        
        for holding in holdings:
            ticker = holding["ticker"]
            shares = holding["shares"]
            purchase_price = holding["purchase_price"]
            
            # Get current price
            price_data = get_price_sync(ticker)
            
            if price_data.get("success") and price_data.get("current_price"):
                current_price = price_data["current_price"]
                daily_change = price_data.get("percent_change", 0)
            else:
                current_price = purchase_price
                daily_change = 0
            
            current_value = shares * current_price
            cost_basis = shares * purchase_price
            total_gain_loss = current_value - cost_basis
            total_pct = ((current_price - purchase_price) / purchase_price * 100) if purchase_price > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            # Format emoji based on performance
            daily_emoji = "📈" if daily_change >= 0 else "📉"
            total_emoji = "✅" if total_gain_loss >= 0 else "❌"
            
            lines.append(f"*{ticker}*: {shares} shares")
            lines.append(f"  💰 ${current_price:.2f} {daily_emoji} {daily_change:+.2f}% today")
            lines.append(f"  {total_emoji} ${total_gain_loss:+.2f} ({total_pct:+.2f}%) total")
            lines.append("")
        
        # Portfolio summary
        portfolio_gain_loss = total_value - total_cost
        portfolio_pct = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        summary_emoji = "🎉" if portfolio_gain_loss >= 0 else "😔"
        
        lines.append("─" * 20)
        lines.append(f"💼 *Total Value*: ${total_value:,.2f}")
        lines.append(f"{summary_emoji} *Total P/L*: ${portfolio_gain_loss:+,.2f} ({portfolio_pct:+.2f}%)")
        lines.append("")
    
    # Watchlist section
    if watchlist:
        lines.append("👀 *Watchlist*")
        lines.append("─" * 20)
        
        for ticker in watchlist:
            price_data = get_price_sync(ticker)
            
            if price_data.get("success") and price_data.get("current_price"):
                current_price = price_data["current_price"]
                daily_change = price_data.get("percent_change", 0)
                emoji = "📈" if daily_change >= 0 else "📉"
                lines.append(f"*{ticker}*: ${current_price:.2f} {emoji} {daily_change:+.2f}%")
            else:
                lines.append(f"*{ticker}*: Price unavailable")
        
        lines.append("")
    
    lines.append("─" * 20)
    lines.append("💬 Reply with any questions about your portfolio!")
    
    return "\n".join(lines)


async def send_daily_update(user_phone: str):
    """
    Send a daily portfolio update to a specific user.
    
    Args:
        user_phone: User's phone number
    """
    settings = get_settings()
    
    try:
        # Generate the update message
        message = format_portfolio_update(user_phone)
        
        if not message:
            logger.info(f"No portfolio or watchlist for {user_phone}, skipping update")
            return
        
        # Send via Twilio
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        client.messages.create(
            body=message,
            from_=settings.twilio_whatsapp_number,
            to=f"whatsapp:{user_phone}"
        )
        
        logger.info(f"Sent daily update to {user_phone}")
        
    except Exception as e:
        logger.error(f"Failed to send daily update to {user_phone}: {str(e)}")


async def send_all_daily_updates():
    """Send daily updates to all registered users."""
    logger.info("Starting daily update job...")
    
    db = get_db()
    users = db.get_all_users_for_updates()
    
    logger.info(f"Sending updates to {len(users)} users")
    
    for user_phone in users:
        await send_daily_update(user_phone)
    
    logger.info("Daily update job completed")


def start_scheduler():
    """Start the APScheduler for daily updates."""
    global _scheduler
    
    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return _scheduler
    
    settings = get_settings()
    
    _scheduler = AsyncIOScheduler()
    
    # Add the daily update job
    _scheduler.add_job(
        send_all_daily_updates,
        CronTrigger(
            hour=settings.daily_update_hour,
            minute=settings.daily_update_minute
        ),
        id="daily_portfolio_update",
        name="Daily Portfolio Update",
        replace_existing=True
    )
    
    _scheduler.start()
    
    logger.info(
        f"Scheduler started. Daily updates scheduled for "
        f"{settings.daily_update_hour:02d}:{settings.daily_update_minute:02d}"
    )
    
    return _scheduler


def stop_scheduler():
    """Stop the scheduler."""
    global _scheduler
    
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler stopped")
