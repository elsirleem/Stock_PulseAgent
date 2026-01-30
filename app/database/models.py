"""
SQLite database models for StockPulse.
"""

import sqlite3
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Base:
    """Base class marker for models."""
    pass


@dataclass
class UserPortfolio(Base):
    """User portfolio holding model."""
    id: Optional[int] = None
    user_phone: str = ""
    ticker: str = ""
    shares: float = 0.0
    purchase_price: float = 0.0
    purchase_date: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Watchlist(Base):
    """User watchlist model."""
    id: Optional[int] = None
    user_phone: str = ""
    ticker: str = ""
    added_at: str = ""


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: str = "stockpulse.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create portfolio table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                ticker TEXT NOT NULL,
                shares REAL NOT NULL,
                purchase_price REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_phone, ticker, purchase_date)
            )
        """)
        
        # Create watchlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                ticker TEXT NOT NULL,
                added_at TEXT NOT NULL,
                UNIQUE(user_phone, ticker)
            )
        """)
        
        # Create users table for daily updates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                daily_updates_enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Portfolio Operations
    def add_stock_to_portfolio(
        self,
        user_phone: str,
        ticker: str,
        shares: float,
        purchase_price: float
    ) -> bool:
        """Add a stock to user's portfolio."""
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO user_portfolio 
                (user_phone, ticker, shares, purchase_price, purchase_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_phone, ticker.upper(), shares, purchase_price, now, now, now))
            conn.commit()
            
            # Also register user for daily updates
            self._ensure_user_exists(user_phone, conn)
            return True
        except sqlite3.IntegrityError:
            # Update existing entry
            cursor.execute("""
                UPDATE user_portfolio 
                SET shares = shares + ?, updated_at = ?
                WHERE user_phone = ? AND ticker = ?
            """, (shares, now, user_phone, ticker.upper()))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def remove_stock_from_portfolio(self, user_phone: str, ticker: str) -> bool:
        """Remove a stock from user's portfolio."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM user_portfolio 
            WHERE user_phone = ? AND ticker = ?
        """, (user_phone, ticker.upper()))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def get_user_portfolio(self, user_phone: str) -> list[dict]:
        """Get all stocks in user's portfolio."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ticker, SUM(shares) as total_shares, 
                   AVG(purchase_price) as avg_price
            FROM user_portfolio 
            WHERE user_phone = ?
            GROUP BY ticker
        """, (user_phone,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "ticker": row["ticker"],
                "shares": row["total_shares"],
                "purchase_price": row["avg_price"]
            }
            for row in rows
        ]
    
    # Watchlist Operations
    def add_to_watchlist(self, user_phone: str, ticker: str) -> bool:
        """Add a stock to user's watchlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO watchlist (user_phone, ticker, added_at)
                VALUES (?, ?, ?)
            """, (user_phone, ticker.upper(), now))
            conn.commit()
            
            # Also register user for daily updates
            self._ensure_user_exists(user_phone, conn)
            return True
        except sqlite3.IntegrityError:
            return False  # Already in watchlist
        finally:
            conn.close()
    
    def remove_from_watchlist(self, user_phone: str, ticker: str) -> bool:
        """Remove a stock from user's watchlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM watchlist 
            WHERE user_phone = ? AND ticker = ?
        """, (user_phone, ticker.upper()))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def get_watchlist(self, user_phone: str) -> list[str]:
        """Get user's watchlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ticker FROM watchlist WHERE user_phone = ?
        """, (user_phone,))
        
        rows = cursor.fetchall()
        conn.close()
        return [row["ticker"] for row in rows]
    
    # User Operations
    def _ensure_user_exists(self, user_phone: str, conn: sqlite3.Connection):
        """Ensure user is registered."""
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO users (phone_number, created_at)
                VALUES (?, ?)
            """, (user_phone, now))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    def get_all_users_for_updates(self) -> list[str]:
        """Get all users with daily updates enabled."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT phone_number FROM users WHERE daily_updates_enabled = 1
        """)
        
        rows = cursor.fetchall()
        conn.close()
        return [row["phone_number"] for row in rows]


# Global database instance
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get the database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def init_db(db_path: str = "stockpulse.db") -> DatabaseManager:
    """Initialize the database."""
    global _db_manager
    _db_manager = DatabaseManager(db_path)
    return _db_manager
