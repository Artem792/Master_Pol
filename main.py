import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings


def save_login_state(username, logged_in=True):
    settings = QSettings("PartnerSystem", "App")
    settings.setValue("logged_in", logged_in)
    if logged_in:
        settings.setValue("user_id", username)
    else:
        settings.setValue("user_id", "")

    config = {
        "logged_in": logged_in,
        "user_id": username if logged_in else ""
    }
    try:
        with open("config.json", 'w') as f:
            json.dump(config, f)
    except:
        pass


def check_authentication():
    settings = QSettings("PartnerSystem", "App")
    is_logged_in = settings.value("logged_in", False, type=bool)
    user_id = settings.value("user_id", "", type=str)

    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                is_logged_in = config.get("logged_in", False)
                user_id = config.get("user_id", "")
        except:
            is_logged_in = False

    if is_logged_in and user_id:
        from database import get_db_connection
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT id FROM managers WHERE login = ?", (user_id,))
                user_exists = cursor.fetchone()
                cursor.close()
                connection.close()

                if user_exists:
                    print(f"Автоматический вход для пользователя: {user_id}")
                    return True
            except:
                pass

    return False


def main():
    app = QApplication(sys.argv)

    if check_authentication():
        print("Запуск главного окна (автоматический вход)...")
        from main_window import MainWindow
        window = MainWindow(save_login_state)
        window.show()
    else:
        print("Запуск окна авторизации...")
        from login_window import LoginWindow
        window = LoginWindow(save_login_state)
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()