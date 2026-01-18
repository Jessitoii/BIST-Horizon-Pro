from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton, QSpinBox, 
    QTabWidget, QMessageBox, QGroupBox, QHeaderView, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from app.models import Stock, PortfolioItem
from PyQt5 import QtWidgets, QtGui
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import datetime

# Charts
class PortfolioDonutChart(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e1e2e') # Match Dark Theme bg
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e2e')

    def update_chart(self, cash, portfolio_items, current_prices):
        self.axes.clear()
        
        labels = ['Cash']
        values = [cash]
        colors = ['#a6e3a1'] # Green for cash
        
        # Calculate value for each stock
        for item in portfolio_items:
            price = current_prices.get(item.symbol, item.average_cost)
            value = item.quantity * price
            if value > 0:
                labels.append(item.symbol)
                values.append(value)
                # Cycle through some nice colors
                colors.append('#89b4fa' if len(colors) % 2 == 0 else '#fab387')

        # Pie Chart
        wedges, texts, autotexts = self.axes.pie(
            values, labels=labels, autopct='%1.1f%%',
            startangle=90, colors=colors,
            textprops=dict(color="w")
        )
        
        # Donut Style
        centre_circle = matplotlib.patches.Circle((0,0), 0.70, fc='#1e1e2e')
        self.fig.gca().add_artist(centre_circle)
        
        self.axes.set_title("Portfolio Allocation", color='#cdd6f4', fontsize=12, fontweight='bold')
        self.fig.canvas.draw()

class EquityLineChart(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e1e2e')
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#252535') # Slightly lighter for chart area
        
        # Style spines
        for spine in self.axes.spines.values():
            spine.set_color('#45475a')
        self.axes.tick_params(colors='#bac2de')
        self.axes.xaxis.label.set_color('#cdd6f4')
        self.axes.yaxis.label.set_color('#cdd6f4')

    def update_chart(self, history_data):
        self.axes.clear()
        self.axes.set_title("Net Worth History", color='#cdd6f4', fontsize=12, fontweight='bold')
        self.axes.grid(True, color='#313244', linestyle='--')
        
        if not history_data:
            self.fig.canvas.draw()
            return

        # Data: list of (timestamp_str, value)
        # Parse timestamp
        times = [datetime.datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S") for row in history_data]
        values = [row['total_value'] for row in history_data]
        
        self.axes.plot(times, values, color='#89b4fa', linewidth=2, marker='o', markersize=4)
        
        # Format Date
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.fig.autofmt_xdate()
        
        self.fig.canvas.draw()


class MarketTableWidget(QTableWidget):
    item_selected = pyqtSignal(object)  # Emits Stock object

    def __init__(self):
        super().__init__()
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels([
            "Symbol", "Price", "High", "Low", "Avg", "Change %", "Cap Lot", "Cap TL"
        ])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.cellClicked.connect(self._on_row_click)
        self.current_stocks = {} # symbol -> Stock

    def update_data(self, stocks: list[Stock]):
        self.setRowCount(len(stocks))
        self.current_stocks = {s.symbol: s for s in stocks}
        
        for i, stock in enumerate(stocks):
            self.setItem(i, 0, QTableWidgetItem(stock.symbol))
            self.setItem(i, 1, QTableWidgetItem(f"{stock.price:.2f}"))
            self.setItem(i, 2, QTableWidgetItem(f"{stock.highest:.2f}"))
            self.setItem(i, 3, QTableWidgetItem(f"{stock.lowest:.2f}"))
            self.setItem(i, 4, QTableWidgetItem(f"{stock.average:.2f}"))
            
            change_item = QTableWidgetItem(f"{stock.percent_change:.2f}%")
            if stock.percent_change > 0:
                change_item.setForeground(Qt.green)
            elif stock.percent_change < 0:
                change_item.setForeground(Qt.red)
            else:
                change_item.setForeground(Qt.lightGray)
                
            self.setItem(i, 5, change_item)
            self.setItem(i, 6, QTableWidgetItem(f"{stock.capacity_lot:,.0f}"))
            self.setItem(i, 7, QTableWidgetItem(f"{stock.capacity_tl:,.0f}"))

    def _on_row_click(self, row, col):
        symbol = self.item(row, 0).text()
        if symbol in self.current_stocks:
            self.item_selected.emit(self.current_stocks[symbol])

class PortfolioWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Symbol", "Quantity", "Avg Cost", "Est. Value"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def update_data(self, items: list[PortfolioItem], current_prices: dict):
        self.setRowCount(len(items))
        for i, item in enumerate(items):
            self.setItem(i, 0, QTableWidgetItem(item.symbol))
            self.setItem(i, 1, QTableWidgetItem(str(item.quantity)))
            self.setItem(i, 2, QTableWidgetItem(f"{item.average_cost:.2f}"))
            
            # Estimated Value
            price = current_prices.get(item.symbol, item.average_cost)
            val = price * item.quantity
            self.setItem(i, 3, QTableWidgetItem(f"{val:,.2f}"))

class TransactionWidget(QGroupBox):
    buy_requested = pyqtSignal(str, int) # symbol, quantity
    sell_requested = pyqtSignal(str, int)

    def __init__(self):
        super().__init__("Trade Operations")
        layout = QVBoxLayout()
        
        self.lbl_selected = QLabel("Selected: None")
        self.lbl_selected.setStyleSheet("font-size: 16px; color: #89b4fa;")
        
        self.lbl_price = QLabel("Price: 0.00")
        self.lbl_price.setStyleSheet("font-size: 14px; color: #a6adc8;")
        
        layout.addWidget(self.lbl_selected)
        layout.addWidget(self.lbl_price)
        
        form = QFormLayout()
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 1000000)
        self.spin_qty.setValue(1)
        form.addRow("Quantity:", self.spin_qty)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        self.btn_buy = QPushButton("Buy")
        self.btn_buy.clicked.connect(self._on_buy)
        self.btn_sell = QPushButton("Sell")
        self.btn_sell.clicked.connect(self._on_sell)
        
        self.btn_buy.setEnabled(False)
        self.btn_sell.setEnabled(False)
        
        btn_layout.addWidget(self.btn_buy)
        btn_layout.addWidget(self.btn_sell)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.current_symbol = None

    def set_selected_stock(self, stock: Stock):
        self.current_symbol = stock.symbol
        self.lbl_selected.setText(f"Selected: {stock.symbol}")
        self.lbl_price.setText(f"Price: {stock.price:.2f}")
        self.btn_buy.setEnabled(True)
        self.btn_sell.setEnabled(True)

    def _on_buy(self):
        if self.current_symbol:
            self.buy_requested.emit(self.current_symbol, self.spin_qty.value())

    def _on_sell(self):
        if self.current_symbol:
            self.sell_requested.emit(self.current_symbol, self.spin_qty.value())

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Stock Market Simulator Pro")
        self.resize(1200, 800)
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget) # Vertical (Header + Tabs)
        
        # 1. Header (Net Worth)
        header_layout = QHBoxLayout()
        self.lbl_net_worth = QLabel("Net Worth: Loading...")
        self.lbl_net_worth.setStyleSheet("font-size: 24px; font-weight: bold; color: #a6e3a1;")
        header_layout.addWidget(self.lbl_net_worth)
        
        self.lbl_cash = QLabel("Cash: Loading...")
        self.lbl_cash.setStyleSheet("font-size: 18px; color: #89b4fa;")
        header_layout.addWidget(self.lbl_cash)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # 2. Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Trade
        trade_tab = QWidget()
        trade_layout = QHBoxLayout(trade_tab)
        
        left_trade = QVBoxLayout()
        self.market_table = MarketTableWidget()
        self.portfolio_table = PortfolioWidget()
        left_trade.addWidget(self.market_table, stretch=2)
        left_trade.addWidget(QLabel("Current Holdings"), stretch=0)
        left_trade.addWidget(self.portfolio_table, stretch=1)
        
        trade_layout.addLayout(left_trade, stretch=3)
        
        right_trade = QVBoxLayout()
        self.transaction_widget = TransactionWidget()
        right_trade.addWidget(self.transaction_widget)
        right_trade.addStretch()
        
        trade_layout.addLayout(right_trade, stretch=1)
        
        self.tabs.addTab(trade_tab, "Trade & Market")
        
        # Tab 2: Analytics
        analytics_tab = QWidget()
        analytics_layout = QHBoxLayout(analytics_tab)
        
        self.donut_chart = PortfolioDonutChart()
        self.line_chart = EquityLineChart()
        
        analytics_layout.addWidget(self.donut_chart)
        analytics_layout.addWidget(self.line_chart)
        
        self.tabs.addTab(analytics_tab, "Analytics")
        
        main_layout.addWidget(self.tabs)

        # Connections
        self.market_table.item_selected.connect(self.transaction_widget.set_selected_stock)
        self.transaction_widget.buy_requested.connect(self.handle_buy)
        self.transaction_widget.sell_requested.connect(self.handle_sell)
        
        # Data Cache
        self.latest_prices = {}
        
        # Refresh Timer for Analytics (Don't update too often)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_charts)
        self.timer.start(5000) # Every 5s
        
        # Initial Refresh
        self.refresh_player_stats()
        self.refresh_charts()

    def update_market(self, stocks: list[Stock]):
        self.market_cache = stocks
        self.latest_prices = {s.symbol: s.price for s in stocks}
        self.market_table.update_data(stocks)
        
        # Update Controller cache for valuation
        self.controller.update_market_cache(stocks)
        
        # Update Portfolio Table live values
        # We need to get portfolio again to update estimated values based on new prices
        portfolio = self.controller.get_portfolio()
        self.portfolio_table.update_data(portfolio, self.latest_prices)

    def refresh_player_stats(self):
        player = self.controller.get_player()
        portfolio = self.controller.get_portfolio()
        
        # Calculate Total Net Worth
        portfolio_val = sum(
            item.quantity * self.latest_prices.get(item.symbol, item.average_cost) 
            for item in portfolio
        )
        net_worth = player.money + portfolio_val
        
        self.lbl_net_worth.setText(f"Net Worth: {net_worth:,.2f} ₺")
        self.lbl_cash.setText(f"Cash: {player.money:,.2f} ₺")
        
        self.portfolio_table.update_data(portfolio, self.latest_prices)

    def refresh_charts(self):
        # Refresh Data
        player = self.controller.get_player()
        portfolio = self.controller.get_portfolio()
        history = self.controller.get_portfolio_history()
        
        self.donut_chart.update_chart(player.money, portfolio, self.latest_prices)
        self.line_chart.update_chart(history)

    def handle_buy(self, symbol, qty):
        stock = self.market_table.current_stocks.get(symbol)
        if not stock:
            QMessageBox.critical(self, "Error", "Market data out of sync.")
            return

        success, msg = self.controller.buy_stock(stock, qty)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.refresh_player_stats()
            self.refresh_charts()
        else:
            QMessageBox.warning(self, "Failed", msg)

    def handle_sell(self, symbol, qty):
        stock = self.market_table.current_stocks.get(symbol)
        if not stock:
            QMessageBox.critical(self, "Error", "Market data out of sync.")
            return

        success, msg = self.controller.sell_stock(stock, qty)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.refresh_player_stats()
            self.refresh_charts()
        else:
            QMessageBox.warning(self, "Failed", msg)
