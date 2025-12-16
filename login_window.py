import sys
import hashlib
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QMessageBox, QHBoxLayout, QFrame)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from database import get_db_connection
from main_window import MainWindow
from partner_edit_window import RegisterWindow


class LoginWindow(QWidget):
    def __init__(self, save_login_callback=None):
        super().__init__()
        self.save_login = save_login_callback
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 320)
        self.setWindowIcon(QIcon("icon.png")) if self._has_icon() else None
        self.init_ui()

    def _has_icon(self):
        import os
        return os.path.exists("icon.png")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel("Вход в систему")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
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
        form_layout.setSpacing(15)

        # Поля ввода
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите ваш логин")
        self.input_login.setFixedHeight(40)
        self.input_login.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setFixedHeight(40)
        self.input_password.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        form_layout.addWidget(QLabel("Логин:"))
        form_layout.addWidget(self.input_login)
        form_layout.addWidget(QLabel("Пароль:"))
        form_layout.addWidget(self.input_password)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.button_login = QPushButton("Войти")
        self.button_login.setFixedHeight(45)
        self.button_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.button_login.clicked.connect(self.login)
        button_layout.addWidget(self.button_login)

        self.button_register = QPushButton("Регистрация")
        self.button_register.setFixedHeight(45)
        self.button_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.button_register.clicked.connect(self.open_register)
        button_layout.addWidget(self.button_register)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def login(self):
        login = self.input_login.text()
        password = self.input_password.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM managers WHERE login = %s AND password_hash = %s",
                           (login, password_hash))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                # Если есть функция сохранения - вызываем ее
                if self.save_login:
                    self.save_login(login, True)

                self.close()
                self.main_window = MainWindow(self.save_login)
                self.main_window.show()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(err)}")

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()