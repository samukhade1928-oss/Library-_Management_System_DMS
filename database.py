import mysql.connector
from mysql.connector import Error


def connect_db():

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="KHADE1928",
            database="library_management"
        )

        if connection.is_connected():
            print("MySQL Database Connected Successfully!")

        return connection

    except Error as e:
        print("Database Connection Error:", e)
        return None