DARK_THEME_QSS = """
/* Global */
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 20px;
    background-color: #252535;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #89b4fa;
}

/* Tables */
QTableWidget {
    background-color: #1e1e2e;
    gridline-color: #313244;
    border: none;
    selection-background-color: #313244;
    selection-color: #cdd6f4;
    outline: none;
}
QTableWidget::item {
    padding: 5px;
    border-bottom: 1px solid #313244;
}
QTableWidget::item:hover {
    background-color: #313244;
}
QHeaderView::section {
    background-color: #252535;
    padding: 5px;
    border: none;
    font-weight: bold;
    color: #bac2de;
}
QTableWidget QTableCornerButton::section {
    background-color: #252535;
    border: none;
}

/* Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px;
    color: #cdd6f4;
}
QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #89b4fa;
}

/* Buttons */
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #74c7ec;
}
QPushButton[text="Sell"] {
    background-color: #f38ba8;
}
QPushButton[text="Sell"]:hover {
    background-color: #eba0ac;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1e1e2e;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #313244;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #252535;
    color: #a6adc8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #313244;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}
QTabBar::tab:hover {
    background: #313244;
    color: #cdd6f4;
}
"""
