import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QFormLayout, QHeaderView)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import get_db_connection
from calculations import calculate_material


class SalesHistoryWindow(QWidget):
    def __init__(self, partner_id):
        super().__init__()
        self.partner_id = partner_id
        self.setWindowTitle(f"История продаж (ID: {partner_id})")
        self.setFixedSize(850, 550)
        self.init_ui()
        self.load_sales_history()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel(f"История продаж партнера ID: {self.partner_id}")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Таблица
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(7)
        self.table_history.setHorizontalHeaderLabels(
            ["ID", "Продукция", "Кол-во", "Дата", "Пар.1", "Пар.2", "Материал"])

        header = self.table_history.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table_history.setAlternatingRowColors(True)
        layout.addWidget(self.table_history)

        # Форма расчета
        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.input_product_type = QLineEdit()
        self.input_product_type.setPlaceholderText("1-5")
        self.input_product_type.setFixedWidth(80)

        self.input_material_type = QLineEdit()
        self.input_material_type.setPlaceholderText("1-5")
        self.input_material_type.setFixedWidth(80)

        self.input_product_count = QLineEdit()
        self.input_product_count.setPlaceholderText("100")
        self.input_product_count.setFixedWidth(80)

        self.input_param1 = QLineEdit()
        self.input_param1.setPlaceholderText("2.5")
        self.input_param1.setFixedWidth(80)

        self.input_param2 = QLineEdit()
        self.input_param2.setPlaceholderText("3.0")
        self.input_param2.setFixedWidth(80)

        form_layout.addRow("Тип продукции ID:", self.input_product_type)
        form_layout.addRow("Тип материала ID:", self.input_material_type)
        form_layout.addRow("Количество:", self.input_product_count)
        form_layout.addRow("Параметр 1:", self.input_param1)
        form_layout.addRow("Параметр 2:", self.input_param2)

        layout.addLayout(form_layout)

        # Кнопки расчета
        calc_layout = QHBoxLayout()
        calc_layout.setSpacing(10)

        self.button_calc = QPushButton("Рассчитать материал")
        self.button_calc.setFixedHeight(35)
        self.button_calc.clicked.connect(self.calculate_material_full)
        calc_layout.addWidget(self.button_calc)

        self.label_result = QLabel("Результат: -")
        calc_layout.addWidget(self.label_result)
        calc_layout.addStretch()

        layout.addLayout(calc_layout)

        # Кнопка закрытия
        self.button_close = QPushButton("Закрыть")
        self.button_close.setFixedHeight(35)
        self.button_close.clicked.connect(self.close)
        layout.addWidget(self.button_close)

        self.setLayout(layout)

    def load_sales_history(self):
        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT ph.id, p.name, ph.quantity, ph.sale_date, ph.param1, ph.param2
                FROM product_history ph
                JOIN products p ON ph.product_id = p.id
                WHERE ph.partner_id = %s 
                ORDER BY ph.sale_date DESC
            """, (self.partner_id,))

            history = cursor.fetchall()
            self.table_history.setRowCount(len(history))

            for row_number, record in enumerate(history):
                for column_number, data in enumerate(record):
                    item = QTableWidgetItem(str(data))
                    if column_number in [2, 4, 5]:  # Числовые колонки
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_history.setItem(row_number, column_number, item)

                # Расчет материала
                material_needed = calculate_material(
                    product_type_id=1,
                    material_type_id=1,
                    product_count=int(record[2]) if record[2] else 0,
                    param1=float(record[4]) if record[4] else 1.0,
                    param2=float(record[5]) if record[5] else 1.0,
                    product_coef=1.5,
                    defect_percent=2.0
                )

                result_item = QTableWidgetItem(f"{material_needed} ед." if material_needed != -1 else "Ошибка")
                result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_history.setItem(row_number, 6, result_item)

            cursor.close()
            connection.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю: {err}")

    def calculate_material_full(self):
        try:
            product_type_id = int(self.input_product_type.text() or "1")
            material_type_id = int(self.input_material_type.text() or "1")
            product_count = int(self.input_product_count.text() or "100")
            param1 = float(self.input_param1.text() or "1.0")
            param2 = float(self.input_param2.text() or "1.0")

            connection = get_db_connection()
            if not connection:
                raise Exception("Нет подключения к БД")

            cursor = connection.cursor()

            cursor.execute("SELECT coefficient FROM product_types WHERE id = %s", (product_type_id,))
            product_coef_result = cursor.fetchone()
            if not product_coef_result:
                QMessageBox.warning(self, "Ошибка", "Тип продукции не найден")
                cursor.close()
                connection.close()
                return

            product_coef = float(product_coef_result[0])

            cursor.execute("SELECT defect_percent FROM material_types WHERE id = %s", (material_type_id,))
            material_defect_result = cursor.fetchone()
            if not material_defect_result:
                QMessageBox.warning(self, "Ошибка", "Тип материала не найден")
                cursor.close()
                connection.close()
                return

            defect_percent = float(material_defect_result[0])

            cursor.close()
            connection.close()

            result = calculate_material(
                product_type_id=product_type_id,
                material_type_id=material_type_id,
                product_count=product_count,
                param1=param1,
                param2=param2,
                product_coef=product_coef,
                defect_percent=defect_percent
            )

            if result == -1:
                self.label_result.setText("Ошибка расчета")
                QMessageBox.warning(self, "Ошибка", "Проверьте введенные данные")
            else:
                self.label_result.setText(f"Необходимо материала: {result} ед.")

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числа")
        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(err)}")