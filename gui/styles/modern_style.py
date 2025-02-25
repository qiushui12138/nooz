class ModernStyle:
    @staticmethod
    def get_style() -> str:
        return """
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 16px;
                padding: 12px;
                background-color: #252526;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
                color: #569cd6;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #848484;
            }
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                gridline-color: #333333;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #569cd6;
                padding: 6px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #094771;
            }
            QLineEdit {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                background-color: #3c3c3c;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border-color: #569cd6;
            }
            QCheckBox {
                spacing: 6px;
                color: #d4d4d4;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #404040;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #569cd6;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                color: #d4d4d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #d4d4d4;
                margin-right: 6px;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1e1e1e;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #569cd6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QSplitter::handle {
                background-color: #333333;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #d4d4d4;
                padding: 12px 20px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #37373d;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            QTableWidget::item:hover {
                background-color: #2d2d2d;
            }
        """

    @staticmethod
    def get_log_table_style() -> str:
        return """
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                font-size: 13px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:hover {
                background-color: #2d2d2d;
            }
        """
