import time
import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QThread, pyqtSignal
from app.models import Stock

class MarketScraperWorker(QThread):
    data_updated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    URL = "http://bigpara.hurriyet.com.tr/borsa/canli-borsa/"

    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        while self._is_running:
            try:
                stocks = self.fetch_data()
                self.data_updated.emit(stocks)
            except Exception as e:
                self.error_occurred.emit(str(e))
            
            # Sleep for 3 seconds before next update
            time.sleep(3)

    def stop(self):
        self._is_running = False
        self.wait()

    def fetch_data(self) -> list[Stock]:
        response = requests.get(self.URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        stocks = []
        
        # Iterate over each stock row
        rows = soup.find_all("ul", {"class": "live-stock-item"})
        
        for row in rows:
            try:
                # Name
                name_li = row.find("li", class_="cell064 tal arrow")
                if not name_li:
                    continue
                
                # The stock name is in the second 'a' tag
                links = name_li.find_all("a")
                if len(links) < 2:
                    continue
                symbol = links[1].text.strip()
                
                # Helper to get text from a specific class
                def get_text(cls_name):
                    node = row.find("li", class_=cls_name)
                    return node.text.strip() if node else "0"

                # Parse values (Turkey format: 1.234,56 -> 1234.56)
                def parse_float(text):
                    try:
                        clean = text.replace(".", "").replace(",", ".")
                        return float(clean)
                    except (ValueError, AttributeError):
                        return 0.0

                price = parse_float(get_text("node-c"))      # Last Price
                highest = parse_float(get_text("node-h"))    # High
                lowest = parse_float(get_text("node-i"))     # Low
                average = parse_float(get_text("node-j"))    # Avg
                percent = parse_float(get_text("node-e"))    # Percent
                cap_lot = parse_float(get_text("node-k"))    # Lot
                cap_tl = parse_float(get_text("node-l"))     # Volume TL

                stock = Stock(
                    symbol=symbol,
                    price=price,
                    highest=highest,
                    lowest=lowest,
                    average=average,
                    percent_change=percent,
                    capacity_lot=cap_lot,
                    capacity_tl=cap_tl
                )
                stocks.append(stock)
                
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        return stocks
