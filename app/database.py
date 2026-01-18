import sqlite3
import os
from contextlib import contextmanager

DB_NAME = "game.db"

class DatabaseManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize the database with necessary tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Player Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    money REAL NOT NULL DEFAULT 1000.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Portfolio Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    average_cost REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (player_id) REFERENCES player (id),
                    UNIQUE(player_id, symbol)
                )
            ''')

            # Portfolio History Table (For Equity Curve)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    total_value REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES player (id)
                )
            ''')
            
            # Create default player if not exists
            cursor.execute('SELECT count(*) FROM player')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO player (money) VALUES (1000.0)')
            
            conn.commit()
