import mysql.connector
from mysql.connector import Error

import os
from dotenv import load_dotenv
import phpserialize

# Load environment variables
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')


def find_user_id(user_id: str):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(
                'SELECT user_id, meta_key, meta_value FROM wp_usermeta WHERE meta_key="uuid" AND meta_value=%s',
                (user_id,
                 ))
            result = cursor.fetchall()
            cursor.close()
            if len(result) != 1:
                return False
            else:
                return result[0][0]

    except Error as e:
        print(f"Error: {e}")


def find_name_(user_id: int, device_id: str, status: str):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(
                'SELECT user_id, meta_key, meta_value FROM wp_usermeta WHERE meta_key="devices" AND user_id=%s',
                (user_id,
                 ))
            result = cursor.fetchone()
            data = phpserialize.loads(result[2].encode(), decode_strings=True)
            name = False
            for item in data.values():
                if item.get("id") == device_id:
                    name = item.get("name")
                    item.update({"status": status})
            if name:
                res = phpserialize.dumps(data).decode("utf-8")
                cursor.execute(
                    '''
                        UPDATE wp_usermeta
                        SET meta_value = %s
                        WHERE user_id = %s AND meta_key = %s
                    ''',
                    (res, user_id, "devices")
                )
                connection.commit()
            cursor.close()
            return name

    except Error as e:
        print(f"Error: {e}")


def find_name(user_id_: str, device_id_: str, status: str):
    user_id = find_user_id(user_id_)
    if user_id:
        return find_name_(user_id, device_id_, status)
    return False
