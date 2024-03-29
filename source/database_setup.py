import psycopg2
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

import logging
from typing import Dict, Union

logging.basicConfig(level=logging.INFO)

class PassesDB:
    def __init__(self, host=None, database=None, user=None, password=None):
        self.connection_params = {
            'host': host or os.getenv('FSTR_DB_HOST', default='localhost'),
            'database': database or os.getenv('FSTR_DB_DATABASE', default='mydatabase'),
            'user': user or os.getenv('FSTR_DB_USER', default='myuser'),
            'password': password or os.getenv('FSTR_DB_PASSWORD', default='')
        }
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            logging.info("Успешное подключение к базе данных")
        except psycopg2.Error as e:
            logging.error(f"Ошибка подключения к базе данных: {e}")
            raise
    def submit_data(self, data: Dict[str, Union[str, int, float]]) -> Dict[str, Union[int, str]]:
        required_fields = ['beauty_title', 'title', 'add_time', 'user', 'coords', 'level', 'images']
        if not all(field in data for field in required_fields):
            return {'status': 400, 'message': 'Отсутствуют обязательные поля в данных', 'id': None}

        numeric_fields = ['latitude', 'longitude', 'height']
        for field in numeric_fields:
            if field in data and not isinstance(data[field], (int, float)):
                return {'status': 400, 'message': f'Поле {field} должно быть числовым значением', 'id': None}

        try:
            with self.conn.cursor() as cursor:
                query = '''
                    INSERT INTO passes
                    (beauty_title, title, other_titles, connect, add_time,
                     user_email, user_fam, user_name, user_otc, user_phone,
                     latitude, longitude, height, winter, summer, autumn, spring, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                '''
                cursor.execute(query, (
                    data['beauty_title'], data['title'], data.get('other_titles', ''),
                    data.get('connect', ''), data['add_time'], data['user']['email'],
                    data['user']['fam'], data['user']['name'], data['user']['otc'],
                    data['user']['phone'], float(data['coords']['latitude']),
                    float(data['coords']['longitude']), int(data['coords']['height']),
                    data['level']['winter'], data['level']['summer'],
                    data['level']['autumn'], data['level']['spring'],
                    data.get('status', 'new')
                ))
                inserted_id = cursor.fetchone()[0]
                self.conn.commit()  # Commit транзакции после успешной вставки
                return {'status': 200, 'message': 'Отправлено успешно', 'id': inserted_id}
        except psycopg2.Error as e:
            self.conn.rollback()  # Rollback транзакции в случае ошибки
            logging.error(f"Ошибка при выполнении операции: {e}")
            return {'status': 500, 'message': f'Ошибка при выполнении операции: {str(e)}', 'id': None, 'field': None}
        except Exception as e:
            logging.error(f"Необработанная ошибка: {e}")
            return {'status': 500, 'message': f'Необработанная ошибка: {str(e)}', 'id': None, 'field': None}

# Создание экземпляра класса PassesDB с использованием значений из конфигурации
db = PassesDB(
    host=os.getenv('FSTR_DB_HOST', default='localhost'),
    database=os.getenv('FSTR_DB_DATABASE', default='mydatabase'),
    user=os.getenv('FSTR_DB_USER', default='myuser'),
    password=os.getenv('FSTR_DB_PASSWORD', default='')
)
data = {
    # ... данные о перевале ...
}
result = db.submit_data(data)
print(result)