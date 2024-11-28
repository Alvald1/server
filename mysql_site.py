import mysql.connector
from mysql.connector import Error

import os
from dotenv import load_dotenv


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
