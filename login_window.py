import sys
import hashlib
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from database import get_db_connection
from register_window import RegisterWindow


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
        main_layout.setContentsMargins(30, 15, 30, 15)
        main_layout.setSpacing(10)

        title = QLabel("Вход в систему")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        main_layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(5)

        top_spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        form_layout.addItem(top_spacer)

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите ваш логин")
        self.input_login.setFixedHeight(46)
        self.input_login.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
                margin-top: 2px;
                margin-bottom: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8fdff;
            }
            QLineEdit:hover {
                border: 2px solid #95a5a6;
            }
        """)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setFixedHeight(46)
        self.input_password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
                margin-top: 2px;
                margin-bottom: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8fdff;
            }
            QLineEdit:hover {
                border: 2px solid #95a5a6;
            }
        """)

        form_layout.addWidget(self.input_login)
        form_layout.addWidget(self.input_password)

        bottom_spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        form_layout.addItem(bottom_spacer)

        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)
        main_layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)

        self.button_login = QPushButton("Войти")
        self.button_login.setFixedHeight(42)
        self.button_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #2c3e50;
            }
        """)
        self.button_login.clicked.connect(self.login)
        button_layout.addWidget(self.button_login)

        self.button_register = QPushButton("Регистрация")
        self.button_register.setFixedHeight(42)
        self.button_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #2c3e50;
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
            cursor.execute("SELECT * FROM managers WHERE login = ? AND password_hash = ?",
                           (login, password_hash))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                if self.save_login:
                    self.save_login(login, True)

                self.close()
                from main_window import MainWindow
                self.main_window = MainWindow(self.save_login)
                self.main_window.show()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(err)}")

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()