# 📈 BIST Horizon Pro

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green) ![Architecture](https://img.shields.io/badge/Architecture-MVC-orange) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

**BIST Horizon Pro** is a comprehensive desktop trading simulation environment tailored for the Borsa Istanbul (BIST100). Designed with a focus on clean architecture and user experience, it allows users to practice trading strategies in real-time without financial risk.

The application features a modern, dark-themed dashboard that mimics professional trading terminals, offering live market data tracking, portfolio management, and historical performance analytics.

## 🚀 Key Features

* **Real-Time Simulation:** Live tracking of BIST100 stock prices, percentage changes, and volume data.
* **Professional Dashboard:** A custom-styled Dark Mode UI built with PyQt5, featuring a responsive layout and high-readability data grids.
* **Portfolio Management:**
    * **Net Worth Tracking:** Real-time calculation of total equity (Cash + Unrealized P&L).
    * **Order Execution:** Instant Buy/Sell operations with dynamic commission calculation.
    * **Holdings Analysis:** View average cost, quantity, and current value of owned assets.
* **Persistent Data:** Uses **SQLite** to securely store user portfolio history, ensuring progress is saved between sessions.
* **Data Visualization:** Interactive charts for portfolio distribution and equity curves (powered by Matplotlib).

## 🛠 Technical Architecture

This project was engineered to demonstrate scalable software design principles:

* **MVC Pattern:** The application logic is strictly separated into **Model** (SQLite/Data Processing), **View** (PyQt5 UI), and **Controller** (Business Logic). This ensures maintainability and testability.
* **Concurrency:** Data fetching runs on separate `QThread` workers to prevent UI freezing during network operations, ensuring a smooth user experience.
* **Custom Styling:** Implements a comprehensive QSS (Qt Style Sheet) system to override default native widgets for a modern look.

### 💡 A Note on Data Acquisition (Web Scraping)

> **Why Web Scraping?**
> Accessing real-time stock market APIs (e.g., Bloomberg, Refinitiv) typically incurs significant enterprise-level costs. To keep this project open-source and accessible for educational purposes, I engineered a custom **Web Scraping Engine** using `BeautifulSoup` and `Requests`.
>
> The engine parses live data from public financial portals (e.g., BigPara) in real-time. It is optimized to parse specific DOM elements (`data-symbol` attributes) rather than fragile text structures, making the scraper robust against minor frontend changes on the source site.

## 📸 Screenshots

| Market Overview | Portfolio & Analytics |
|:---:|:---:|
| ![Market View](image_7f0fc5.png) | ![Dark Mode Dashboard](image_8900a9.png) |

*(Note: Replace `image_*.png` with the actual paths to your screenshots in the repo)*

## 📦 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Jessitoii/BIST-Horizon-Pro.git](https://github.com/Jessitoii/BIST-Horizon-Pro.git)
    cd stock-market-simulator
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## 🗺 Roadmap

* [ ] Integration of technical indicators (RSI, MACD) to the scraping engine.
* [ ] User authentication system for multiple portfolios.
* [ ] Exporting trade history to CSV/Excel.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
*Developed by [Alper](https://github.com/Jessitoii) - Computer Engineering Student*