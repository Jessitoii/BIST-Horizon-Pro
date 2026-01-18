from app.database import DatabaseManager
from app.models import PlayerModel, PortfolioItem, Stock

class GameController:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.player_id = 1 # Single player for now

    def get_player(self) -> PlayerModel:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player WHERE id = ?", (self.player_id,))
            row = cursor.fetchone()
            if row:
                return PlayerModel(id=row['id'], money=row['money'])
            return PlayerModel(id=0, money=0.0)

    def get_portfolio(self) -> list[PortfolioItem]:
        items = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM portfolio WHERE player_id = ?", (self.player_id,))
            rows = cursor.fetchall()
            for row in rows:
                items.append(PortfolioItem(
                    symbol=row['symbol'],
                    quantity=row['quantity'],
                    average_cost=row['average_cost']
                ))
        return items

    def buy_stock(self, stock: Stock, quantity: int) -> tuple[bool, str]:
        if quantity <= 0:
            return False, "Quantity must be positive."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check Balance
            cursor.execute("SELECT money FROM player WHERE id = ?", (self.player_id,))
            current_money = cursor.fetchone()['money']
            
            total_cost = (stock.price * quantity) + stock.commission
            
            if current_money < total_cost:
                return False, f"Insufficient funds. Need {total_cost:.2f}, have {current_money:.2f}."
            
            # Deduct Money
            new_money = current_money - total_cost
            cursor.execute("UPDATE player SET money = ? WHERE id = ?", (new_money, self.player_id))
            
            # Update Portfolio
            cursor.execute("SELECT * FROM portfolio WHERE player_id = ? AND symbol = ?", (self.player_id, stock.symbol))
            existing = cursor.fetchone()
            
            if existing:
                new_qty = existing['quantity'] + quantity
                # simple avg cost calculation: (old_total_cost + new_cost) / new_qty
                # Note: commission is usually expense, not cost basis, but depends on accounting. 
                # Let's count price only for cost basis to keep it simple, or include commission? 
                # Simpler: ((old_qty * old_avg) + (new_qty * price)) / total_qty
                
                current_total_value = existing['quantity'] * existing['average_cost']
                new_purchase_value = quantity * stock.price
                new_avg = (current_total_value + new_purchase_value) / new_qty
                
                cursor.execute("""
                    UPDATE portfolio 
                    SET quantity = ?, average_cost = ? 
                    WHERE player_id = ? AND symbol = ?
                """, (new_qty, new_avg, self.player_id, stock.symbol))
            else:
                cursor.execute("""
                    INSERT INTO portfolio (player_id, symbol, quantity, average_cost)
                    VALUES (?, ?, ?, ?)
                """, (self.player_id, stock.symbol, quantity, stock.price))
            
            conn.commit()
            
            # Record history
            self.snapshot_portfolio_value(conn)
            
            return True, "Purchase successful."

    def sell_stock(self, stock: Stock, quantity: int) -> tuple[bool, str]:
        if quantity <= 0:
            return False, "Quantity must be positive."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check Ownership
            cursor.execute("SELECT * FROM portfolio WHERE player_id = ? AND symbol = ?", (self.player_id, stock.symbol))
            existing = cursor.fetchone()
            
            if not existing or existing['quantity'] < quantity:
                return False, "Not enough shares to sell."
            
            # Calculate Revenue
            revenue = (stock.price * quantity) - stock.commission
            
            # Update Money
            cursor.execute("SELECT money FROM player WHERE id = ?", (self.player_id,))
            current_money = cursor.fetchone()['money']
            cursor.execute("UPDATE player SET money = ? WHERE id = ?", (current_money + revenue, self.player_id))
            
            # Update Portfolio
            new_qty = existing['quantity'] - quantity
            if new_qty == 0:
                cursor.execute("DELETE FROM portfolio WHERE player_id = ? AND symbol = ?", (self.player_id, stock.symbol))
            else:
                cursor.execute("UPDATE portfolio SET quantity = ? WHERE player_id = ? AND symbol = ?", 
                               (new_qty, self.player_id, stock.symbol))
            
            conn.commit()
            
            # Record history
            self.snapshot_portfolio_value(conn)

            return True, "Sale successful."

    def update_market_cache(self, stocks: list[Stock]):
        """Cache latest prices for accurate portfolio valuation."""
        self.price_cache = {s.symbol: s.price for s in stocks}

    def snapshot_portfolio_value(self, conn=None):
        """Calculates total net worth and records it."""
        # Note: If no price cache, we use average_cost (better than nothing).
        # Ideally, we should have the latest prices.
        
        should_close = False
        if conn is None:
            conn = sqlite3.connect(self.db.db_name)
            conn.row_factory = sqlite3.Row
            should_close = True

        try:
            cursor = conn.cursor()
            
            # Get Money
            cursor.execute("SELECT money FROM player WHERE id = ?", (self.player_id,))
            row = cursor.fetchone()
            money = row['money'] if row else 0.0
            
            # Get Portfolio
            cursor.execute("SELECT * FROM portfolio WHERE player_id = ?", (self.player_id,))
            items = cursor.fetchall()
            
            portfolio_value = 0.0
            for item in items:
                symbol = item['symbol']
                qty = item['quantity']
                # Use cached price if available, else cost
                price = getattr(self, 'price_cache', {}).get(symbol, item['average_cost'])
                portfolio_value += qty * price
                
            total_net_worth = money + portfolio_value
            
            cursor.execute("INSERT INTO portfolio_history (player_id, total_value) VALUES (?, ?)", 
                           (self.player_id, total_net_worth))
            if should_close:
                conn.commit()
        finally:
            if should_close:
                conn.close()

    def get_portfolio_history(self) -> list[tuple]:
        """Returns list of (timestamp, value)."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, total_value FROM portfolio_history WHERE player_id = ? ORDER BY timestamp ASC", (self.player_id,))
            return cursor.fetchall()
