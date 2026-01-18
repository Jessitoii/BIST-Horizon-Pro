import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from app.database import DatabaseManager
from app.controllers import GameController
from app.views import MainWindow
from app.services import MarketScraperWorker

from app.styles import DARK_THEME_QSS

def main():
    # 1. Setup Application
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    app.setStyleSheet(DARK_THEME_QSS) 

    # 2. Initialize Database
    db_manager = DatabaseManager()
    try:
        db_manager.init_db()
    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Failed to initialize database: {e}")
        sys.exit(1)

    # 3. Initialize Controller
    controller = GameController(db_manager)

    # 4. Initialize View
    window = MainWindow(controller)
    window.show()

    # 5. Initialize Background Service
    scraper_worker = MarketScraperWorker()
    
    # Connect signals
    scraper_worker.data_updated.connect(window.update_market)
    
    def on_scraper_error(err):
        # We might not want to verify block with a popup loop if it spams,
        # but for now let's just log to status bar or print
        window.statusBar().showMessage(f"Network Error: {err}")

    scraper_worker.error_occurred.connect(on_scraper_error)

    # Start scraper
    scraper_worker.start()

    # 6. Run Loop
    exit_code = app.exec_()
    
    # Cleanup
    scraper_worker.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
