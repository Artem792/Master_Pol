# database.py
import sqlite3
from sqlite3 import Error
import os


def get_db_connection():
    """Создание подключения к SQLite базе данных"""
    try:
        # База данных будет в файле в той же директории
        db_path = "master_pol_db.sqlite"

        # Создаем подключение
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row  # Для доступа к столбцам по имени

        # Включаем поддержку внешних ключей
        connection.execute("PRAGMA foreign_keys = ON")

        # Создаем таблицы, если их нет
        create_tables(connection)

        return connection
    except Error as e:
        print(f"Ошибка подключения к БД SQLite: {e}")
        return None


def create_tables(connection):
    """Создание всех необходимых таблиц"""
    cursor = connection.cursor()

    # Таблица менеджеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица партнеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            rating INTEGER DEFAULT 0,
            address TEXT,
            director_name TEXT,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица типов продукции
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            coefficient REAL NOT NULL DEFAULT 1.00
        )
    ''')

    # Таблица типов материалов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS material_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            defect_percent REAL NOT NULL DEFAULT 0.00
        )
    ''')

    # Таблица продуктов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type_id INTEGER NOT NULL,
            material_type_id INTEGER NOT NULL,
            FOREIGN KEY (product_type_id) REFERENCES product_types(id) ON DELETE CASCADE,
            FOREIGN KEY (material_type_id) REFERENCES material_types(id) ON DELETE CASCADE
        )
    ''')

    # Таблица истории продаж
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            param1 REAL NOT NULL DEFAULT 1.00,
            param2 REAL NOT NULL DEFAULT 1.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    ''')

    # Триггер для обновления updated_at в partners
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_partners_timestamp 
        AFTER UPDATE ON partners
        BEGIN
            UPDATE partners SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    ''')

    # Создаем тестовые данные, если таблицы пустые
    initialize_test_data(connection)

    connection.commit()


def initialize_test_data(connection):
    """Инициализация тестовых данных при первом запуске"""
    cursor = connection.cursor()
    import hashlib

    # Проверяем, есть ли менеджеры
    cursor.execute("SELECT COUNT(*) FROM managers")
    if cursor.fetchone()[0] == 0:
        # Создаем администратора
        password_hash = hashlib.sha256("admin".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO managers (login, password_hash) VALUES (?, ?)",
            ("admin", password_hash)
        )
        print("Создан администратор: логин=admin, пароль=admin")

    # Проверяем, есть ли типы продукции
    cursor.execute("SELECT COUNT(*) FROM product_types")
    if cursor.fetchone()[0] == 0:
        product_types = [
            ("Стандартная продукция", 1.0),
            ("Премиум продукция", 1.5),
            ("Эконом продукция", 0.8),
            ("Специальная продукция", 2.0),
            ("Экспортная продукция", 1.2)
        ]
        for name, coeff in product_types:
            cursor.execute(
                "INSERT INTO product_types (name, coefficient) VALUES (?, ?)",
                (name, coeff)
            )

    # Проверяем, есть ли типы материалов
    cursor.execute("SELECT COUNT(*) FROM material_types")
    if cursor.fetchone()[0] == 0:
        material_types = [
            ("Основной материал", 2.0),
            ("Вспомогательный материал", 5.0),
            ("Упаковочный материал", 3.0),
            ("Спецматериал", 1.5),
            ("Импортный материал", 2.5)
        ]
        for name, defect in material_types:
            cursor.execute(
                "INSERT INTO material_types (name, defect_percent) VALUES (?, ?)",
                (name, defect)
            )

    # Проверяем, есть ли продукты
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Продукт А", 1, 1),
            ("Продукт Б", 2, 2),
            ("Продукт В", 3, 3),
            ("Продукт Г", 4, 4),
            ("Продукт Д", 5, 5)
        ]
        for name, p_type, m_type in products:
            cursor.execute(
                "INSERT INTO products (name, product_type_id, material_type_id) VALUES (?, ?, ?)",
                (name, p_type, m_type)
            )

    # Проверяем, есть ли партнеры
    cursor.execute("SELECT COUNT(*) FROM partners")
    if cursor.fetchone()[0] == 0:
        partners = [
            ("ООО 'ТехноПром'", "Поставщик", 8, "г. Москва, ул. Промышленная, 15", "Иванов И.И.", "+7(495)123-45-67",
             "info@technoprom.ru"),
            ("ИП Петров", "Дистрибьютор", 6, "г. Санкт-Петербург, пр. Невский, 100", "Петров П.П.", "+7(812)234-56-78",
             "petrov@mail.ru"),
            ("ЗАО 'СтройМаш'", "Подрядчик", 9, "г. Екатеринбург, ул. Машиностроителей, 25", "Сидоров С.С.",
             "+7(343)345-67-89", "stroymash@yandex.ru"),
            (
            "АО 'ТоргСервис'", "Дистрибьютор", 7, "г. Новосибирск, ул. Ленина, 50", "Кузнецов К.К.", "+7(383)456-78-90",
            "torgserv@gmail.com"),
            ("ООО 'ПромСнаб'", "Поставщик", 5, "г. Казань, ул. Баумана, 30", "Алексеев А.А.", "+7(843)567-89-01",
             "promsnab@mail.ru")
        ]
        for name, p_type, rating, address, director, phone, email in partners:
            cursor.execute(
                """INSERT INTO partners (name, type, rating, address, director_name, phone, email) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, p_type, rating, address, director, phone, email)
            )

    # Проверяем, есть ли история продаж
    cursor.execute("SELECT COUNT(*) FROM product_history")
    if cursor.fetchone()[0] == 0:
        from datetime import date, timedelta
        today = date.today()

        # Создаем тестовые продажи
        for i in range(1, 6):
            for j in range(1, 4):
                sale_date = today - timedelta(days=j * 30)
                cursor.execute(
                    """INSERT INTO product_history 
                       (partner_id, product_id, quantity, sale_date, param1, param2) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (i, j, i * 100, sale_date.isoformat(), 1.0 + i * 0.2, 1.0 + j * 0.1)
                )

    connection.commit()