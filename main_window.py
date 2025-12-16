import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout,
                             QHeaderView, QLabel, QFrame)
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtCore import Qt
from database import get_db_connection
from partner_edit_window import PartnerEditWindow
from sales_history_window import SalesHistoryWindow


class MainWindow(QMainWindow):
    def __init__(self, save_login_callback):
        super().__init__()
        self.save_login = save_login_callback
        self.setWindowTitle("Управление партнерами")
        self.setGeometry(100, 100, 1100, 600)
        self.setWindowIcon(QIcon("icon.png")) if self._has_icon() else None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        header_layout = QHBoxLayout()
        title = QLabel("📋 Список партнеров")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.button_refresh = QPushButton("🔄 Обновить")
        self.button_refresh.setFixedWidth(120)
        self.button_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.button_refresh.clicked.connect(self.load_partners)
        header_layout.addWidget(self.button_refresh)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Таблица
        self.table_partners = QTableWidget()
        self.table_partners.setColumnCount(6)
        self.table_partners.setHorizontalHeaderLabels(["ID", "Название", "Тип", "Рейтинг", "Телефон", "Скидка"])

        # Стиль таблицы
        self.table_partners.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f1f1f1;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)

        header = self.table_partners.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table_partners.setAlternatingRowColors(True)
        self.table_partners.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table_partners)

        # Панель действий
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        buttons = [
            ("➕ Добавить", self.open_add_partner, "#2ecc71"),
            ("✏️ Редактировать", self.open_edit_partner, "#3498db"),
            ("📊 История продаж", self.open_sales_history, "#e67e22"),
            ("🚪 Выйти", self.logout, "#e74c3c")
        ]

        for text, handler, color in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0 15px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                }}
                QPushButton:disabled {{
                    background-color: #95a5a6;
                }}
            """)
            btn.clicked.connect(handler)
            action_layout.addWidget(btn)

        action_frame.setLayout(action_layout)
        main_layout.addWidget(action_frame)

        central_widget.setLayout(main_layout)
        self.load_partners()

    def _darken_color(self, hex_color):
        # Простое затемнение цвета
        colors = {
            "#2ecc71": "#27ae60",
            "#3498db": "#2980b9",
            "#e67e22": "#d35400",
            "#e74c3c": "#c0392b"
        }
        return colors.get(hex_color, hex_color)

    def _has_icon(self):
        import os
        return os.path.exists("icon.png")

    def load_partners(self):
        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, type, rating, phone FROM partners ORDER BY name")
            partners = cursor.fetchall()
            self.table_partners.setRowCount(0)

            for row_number, partner in enumerate(partners):
                partner_id = partner[0]
                self.table_partners.insertRow(row_number)

                for column_number, data in enumerate(partner):
                    item = QTableWidgetItem(str(data))
                    if column_number == 3:  # Рейтинг
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        rating = int(data) if data else 0
                        if rating >= 8:
                            item.setBackground(QColor(46, 204, 113, 50))
                            item.setForeground(QColor(39, 174, 96))
                        elif rating >= 5:
                            item.setBackground(QColor(241, 196, 15, 50))
                            item.setForeground(QColor(243, 156, 18))
                        else:
                            item.setBackground(QColor(231, 76, 60, 50))
                            item.setForeground(QColor(192, 57, 43))
                    self.table_partners.setItem(row_number, column_number, item)

                # Расчет скидки
                cursor.execute("SELECT SUM(quantity) FROM product_history WHERE partner_id = %s", (partner_id,))
                total_sales = cursor.fetchone()[0] or 0

                if total_sales < 10000:
                    discount = "0%"
                    color = QColor(149, 165, 166, 50)
                elif total_sales < 50000:
                    discount = "5%"
                    color = QColor(52, 152, 219, 50)
                elif total_sales < 300000:
                    discount = "10%"
                    color = QColor(155, 89, 182, 50)
                else:
                    discount = "15%"
                    color = QColor(46, 204, 113, 50)

                discount_item = QTableWidgetItem(discount)
                discount_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                discount_item.setBackground(color)
                discount_item.setFont(QFont("", 10, QFont.Weight.Bold))
                self.table_partners.setItem(row_number, 5, discount_item)

            cursor.close()
            connection.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {err}")

    def open_add_partner(self):
        self.add_window = PartnerEditWindow()
        self.add_window.show()

    def open_edit_partner(self):
        selected_row = self.table_partners.currentRow()
        if selected_row >= 0:
            partner_id = self.table_partners.item(selected_row, 0).text()
            self.edit_window = PartnerEditWindow(partner_id=int(partner_id))
            self.edit_window.show()
        else:
            QMessageBox.warning(self, "Внимание", "Выберите партнера для редактирования")

    def open_sales_history(self):
        selected_row = self.table_partners.currentRow()
        if selected_row >= 0:
            partner_id = self.table_partners.item(selected_row, 0).text()
            self.history_window = SalesHistoryWindow(partner_id=int(partner_id))
            self.history_window.show()
        else:
            QMessageBox.warning(self, "Внимание", "Выберите партнера для просмотра истории")

    def logout(self):
        from login_window import LoginWindow

        reply = QMessageBox.question(self, "Выход",
                                     "Вы действительно хотите выйти из системы?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Сбрасываем сохраненную авторизацию
            self.save_login("", False)

            self.close()
            self.login_window = LoginWindow(self.save_login)
            self.login_window.show()