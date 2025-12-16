import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox)
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

        self.setFixedSize(400, 450)
        self.init_ui()
        if partner_id:
            self.load_partner_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Данные партнера")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Поля формы
        fields = [
            ("Название *", "input_name", True),
            ("Тип партнера", "input_type", False),
            ("Рейтинг", "input_rating", False),
            ("Адрес", "input_address", False),
            ("ФИО директора", "input_director", False),
            ("Телефон", "input_phone", False),
            ("Email", "input_email", False)
        ]

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Обязательное поле")

        self.input_type = QComboBox()
        self.input_type.addItems(["Поставщик", "Подрядчик", "Дистрибьютор", "Другой"])

        self.input_rating = QLineEdit()
        self.input_rating.setPlaceholderText("0-10")

        self.input_address = QLineEdit()
        self.input_director = QLineEdit()
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("+7 XXX XXX-XX-XX")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("example@mail.ru")

        # Добавление полей
        layout.addWidget(QLabel("Название *:"))
        layout.addWidget(self.input_name)
        layout.addWidget(QLabel("Тип партнера:"))
        layout.addWidget(self.input_type)
        layout.addWidget(QLabel("Рейтинг (0-10):"))
        layout.addWidget(self.input_rating)
        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(self.input_address)
        layout.addWidget(QLabel("ФИО директора:"))
        layout.addWidget(self.input_director)
        layout.addWidget(QLabel("Телефон:"))
        layout.addWidget(self.input_phone)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.input_email)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.button_save = QPushButton("Сохранить")
        self.button_save.setFixedHeight(35)
        self.button_save.clicked.connect(self.save_partner)
        button_layout.addWidget(self.button_save)

        self.button_cancel = QPushButton("Отмена")
        self.button_cancel.setFixedHeight(35)
        self.button_cancel.clicked.connect(self.close)
        button_layout.addWidget(self.button_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_partner_data(self):
        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM partners WHERE id = %s", (self.partner_id,))
            partner = cursor.fetchone()
            cursor.close()
            connection.close()

            if partner:
                self.input_name.setText(partner[1])
                index = self.input_type.findText(partner[2])
                if index >= 0:
                    self.input_type.setCurrentIndex(index)
                self.input_rating.setText(str(partner[3]))
                self.input_address.setText(partner[4])
                self.input_director.setText(partner[5])
                self.input_phone.setText(partner[6])
                self.input_email.setText(partner[7])

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", str(err))

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
            if rating_int < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рейтинг должен быть целым неотрицательным числом")
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
                    SET name=%s, type=%s, rating=%s, address=%s, director_name=%s, phone=%s, email=%s 
                    WHERE id=%s
                """, (name, p_type, rating_int, address, director, phone, email, self.partner_id))
                message = "Данные обновлены"
            else:
                cursor.execute("""
                    INSERT INTO partners (name, type, rating, address, director_name, phone, email) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, p_type, rating_int, address, director, phone, email))
                message = "Партнер добавлен"

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех", message)
            self.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", str(err))


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(350, 280)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Регистрация нового пользователя")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Поля
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Придумайте логин")

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Придумайте пароль")

        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.setPlaceholderText("Повторите пароль")

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.input_login)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.input_password)
        layout.addWidget(QLabel("Подтверждение:"))
        layout.addWidget(self.input_confirm)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.button_register = QPushButton("Зарегистрировать")
        self.button_register.setFixedHeight(35)
        self.button_register.clicked.connect(self.register)
        button_layout.addWidget(self.button_register)

        self.button_cancel = QPushButton("Отмена")
        self.button_cancel.setFixedHeight(35)
        self.button_cancel.clicked.connect(self.close)
        button_layout.addWidget(self.button_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def register(self):
        login = self.input_login.text()
        password = self.input_password.text()
        confirm = self.input_confirm.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        connection = get_db_connection()
        if not connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO managers (login, password_hash) VALUES (%s, %s)",
                           (login, password_hash))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех", "Регистрация успешно завершена")
            self.close()

        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(err)}")