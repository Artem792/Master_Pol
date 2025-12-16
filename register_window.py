# register_window.py
import sys
import hashlib
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import get_db_connection


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(420, 380)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("Регистрация нового пользователя")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(13)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        main_layout.addWidget(title)

        # Карточка формы
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(10)

        # Стиль для меток
        label_style = """
            QLabel {
                font-weight: bold;
                color: #34495e;
                margin-bottom: 4px;
                font-size: 11px;
            }
        """

        # Поля
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Логин")
        self.input_login.setFixedHeight(30)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Пароль")
        self.input_password.setFixedHeight(30)

        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setPlaceholderText("Повторите пароль")
        self.input_confirm.setFixedHeight(30)

        # Общий стиль для полей
        input_style = """
            QLineEdit {
                padding: 7px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
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

        self.input_login.setStyleSheet(input_style)
        self.input_password.setStyleSheet(input_style)
        self.input_confirm.setStyleSheet(input_style)

        # Добавление полей
        labels = ["Логин:", "Пароль:", "Подтверждение:"]
        inputs = [self.input_login, self.input_password, self.input_confirm]

        for label_text, input_field in zip(labels, inputs):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            form_layout.addWidget(label)
            form_layout.addWidget(input_field)
            form_layout.addSpacing(3)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.button_register = QPushButton("👤 Зарегистрировать")
        self.button_register.setFixedHeight(38)
        self.button_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.button_register.clicked.connect(self.register)
        button_layout.addWidget(self.button_register)

        self.button_cancel = QPushButton("❌ Отмена")
        self.button_cancel.setFixedHeight(38)
        self.button_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
                padding: 0 18px;
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

    def validate_login(self, login):
        """Валидация логина"""
        if not login:
            return "Логин не может быть пустым"

        if len(login) < 3:
            return "Логин должен быть не менее 3 символов"

        # Проверка на повторяющиеся буквы (например, "aaa")
        if len(set(login)) == 1 and len(login) > 1:
            return "Логин не может состоять из одинаковых символов"

        # Проверка на только латинские буквы и цифры
        if not re.match(r'^[a-zA-Z0-9_]+$', login):
            return "Логин может содержать только латинские буквы, цифры и символ _"

        # Проверка на слишком простой логин
        simple_logins = ['admin', 'user', 'test', 'guest', 'root', 'manager']
        if login.lower() in simple_logins:
            return "Этот логин слишком распространен, выберите другой"

        return None  # Валидация пройдена

    def validate_password(self, password):
        """Валидация пароля"""
        if not password:
            return "Пароль не может быть пустым"

        if len(password) < 6:
            return "Пароль должен быть не менее 6 символов"

        # Проверка на русские буквы
        if re.search(r'[а-яА-Я]', password):
            return "Пароль не должен содержать русские буквы"

        # Проверка на наличие цифр
        if not re.search(r'\d', password):
            return "Пароль должен содержать хотя бы одну цифру"

        # Проверка на наличие букв
        if not re.search(r'[a-zA-Z]', password):
            return "Пароль должен содержать хотя бы одну букву"

        # Проверка на слишком простой пароль
        simple_passwords = ['123456', 'password', 'qwerty', 'admin123', '000000']
        if password.lower() in simple_passwords:
            return "Этот пароль слишком простой, выберите другой"

        return None  # Валидация пройдена

    def register(self):
        login = self.input_login.text().strip()
        password = self.input_password.text()
        confirm = self.input_confirm.text()

        # Валидация логина
        login_error = self.validate_login(login)
        if login_error:
            QMessageBox.warning(self, "Ошибка логина", login_error)
            self.input_login.setFocus()
            return

        # Валидация пароля
        password_error = self.validate_password(password)
        if password_error:
            QMessageBox.warning(self, "Ошибка пароля", password_error)
            self.input_password.setFocus()
            return

        # Проверка совпадения паролей
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            self.input_confirm.setFocus()
            return

        # Хеширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Подключение к базе данных
        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            # Проверяем, нет ли уже такого логина
            cursor.execute("SELECT id FROM managers WHERE login = ?", (login,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
                self.input_login.setFocus()
                return

            # Создаем нового пользователя
            cursor.execute("INSERT INTO managers (login, password_hash) VALUES (?, ?)",
                           (login, password_hash))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех", "✅ Регистрация успешно завершена")
            self.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(err)}")