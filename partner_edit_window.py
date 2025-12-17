import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import get_db_connection

class PartnerEditWindow(QWidget):
    def __init__(self, partner_id=None):
        super().__init__()
        self.partner_id = partner_id

        if partner_id:
            self.setWindowTitle("Редактирование партнера")
        else:
            self.setWindowTitle("Новый партнер")

        self.setFixedSize(500, 550)
        self.init_ui()
        if partner_id:
            self.load_partner_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        title = QLabel("Данные партнера")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 25px;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)

        label_style = """
            QLabel {
                font-weight: bold;
                color: #34495e;
                margin-bottom: 5px;
                font-size: 12px;
            }
        """

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Введите название партнера")
        self.input_name.setFixedHeight(36)

        self.input_type = QComboBox()
        self.input_type.addItems(["Поставщик", "Подрядчик", "Дистрибьютор", "Другой"])
        self.input_type.setFixedHeight(36)
        self.input_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #95a5a6;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
        """)

        self.input_rating = QLineEdit()
        self.input_rating.setPlaceholderText("0-10")
        self.input_rating.setFixedHeight(36)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Введите адрес")
        self.input_address.setFixedHeight(36)

        self.input_director = QLineEdit()
        self.input_director.setPlaceholderText("Введите ФИО директора")
        self.input_director.setFixedHeight(36)

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        self.input_phone.setFixedHeight(36)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("example@mail.ru")
        self.input_email.setFixedHeight(36)

        input_style = """
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8fdff;
            }
            QLineEdit:hover {
                border: 2px solid #95a5a6;
            }
        """

        self.input_name.setStyleSheet(input_style)
        self.input_rating.setStyleSheet(input_style)
        self.input_address.setStyleSheet(input_style)
        self.input_director.setStyleSheet(input_style)
        self.input_phone.setStyleSheet(input_style)
        self.input_email.setStyleSheet(input_style)

        fields = [
            ("Название *", self.input_name),
            ("Тип партнера", self.input_type),
            ("Рейтинг (0-10)", self.input_rating),
            ("Адрес", self.input_address),
            ("ФИО директора", self.input_director),
            ("Телефон", self.input_phone),
            ("Email", self.input_email)
        ]

        for label_text, widget in fields:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            form_layout.addWidget(label)
            form_layout.addWidget(widget)
            form_layout.addSpacing(5)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.button_save = QPushButton("Сохранить")
        self.button_save.setFixedHeight(42)
        self.button_save.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.button_save.clicked.connect(self.save_partner)
        button_layout.addWidget(self.button_save)

        self.button_cancel = QPushButton("Отмена")
        self.button_cancel.setFixedHeight(42)
        self.button_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.button_cancel.clicked.connect(self.close)
        button_layout.addWidget(self.button_cancel)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_partner_data(self):
        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM partners WHERE id = ?", (self.partner_id,))
            partner = cursor.fetchone()
            cursor.close()
            connection.close()

            if partner:
                columns = ['id', 'name', 'type', 'rating', 'address',
                           'director_name', 'phone', 'email', 'created_at', 'updated_at']

                partner_dict = {}
                for i, col in enumerate(columns):
                    if i < len(partner):
                        partner_dict[col] = partner[i]
                    else:
                        partner_dict[col] = ''

                self.input_name.setText(str(partner_dict.get('name', '')))

                type_text = str(partner_dict.get('type', ''))
                if type_text:
                    index = self.input_type.findText(type_text)
                    if index >= 0:
                        self.input_type.setCurrentIndex(index)

                rating_value = partner_dict.get('rating', 0)
                self.input_rating.setText(str(rating_value) if rating_value not in [None, ''] else '0')

                self.input_address.setText(str(partner_dict.get('address', '')))
                self.input_director.setText(str(partner_dict.get('director_name', '')))
                self.input_phone.setText(str(partner_dict.get('phone', '')))
                self.input_email.setText(str(partner_dict.get('email', '')))

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(err)}")

    def save_partner(self):
        name = self.input_name.text().strip()
        p_type = self.input_type.currentText()
        rating = self.input_rating.text().strip()
        address = self.input_address.text().strip()
        director = self.input_director.text().strip()
        phone = self.input_phone.text().strip()
        email = self.input_email.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return

        try:
            rating_int = int(rating) if rating else 0
            if rating_int < 0 or rating_int > 10:
                QMessageBox.warning(self, "Ошибка", "Рейтинг должен быть от 0 до 10")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рейтинг должен быть целым числом")
            return

        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            if self.partner_id:
                cursor.execute("""
                    UPDATE partners 
                    SET name=?, type=?, rating=?, address=?, director_name=?, phone=?, email=? 
                    WHERE id=?
                """, (name, p_type, rating_int, address, director, phone, email, self.partner_id))
                message = "Данные партнера обновлены"
            else:
                cursor.execute("""
                    INSERT INTO partners (name, type, rating, address, director_name, phone, email) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, p_type, rating_int, address, director, phone, email))
                message = "Новый партнер добавлен"

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех", message)
            self.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(err)}")