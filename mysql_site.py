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

try:
    # Establish the connection
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )

    if connection.is_connected():
        print("Connected to the database")
        # Create a cursor
        cursor = connection.cursor()
        # Execute the query
        cursor.execute('SELECT * FROM wp_users LIMIT 5')
        # Fetch and print results
        result = cursor.fetchall()
        for row in result:
            print(row)
        # Close the cursor
        cursor.close()

except Error as e:
    print(f"Error: {e}")

finally:
    # Ensure the connection is closed
    if connection.is_connected():
        connection.close()
        print("Database connection closed")

