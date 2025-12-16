import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='master_pol_db'
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None