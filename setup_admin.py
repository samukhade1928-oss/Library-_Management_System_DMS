from database import connect_db
from auth import hash_password
from getpass import getpass

username = input("Enter Admin Username: ")
password = getpass("Enter Admin Password: ")

db = connect_db()

if db:

    cursor = db.cursor()

    try:
        password_hash = hash_password(password)

        query = """
        INSERT INTO admin (username, password_hash)
        VALUES (%s, %s)
        """

        cursor.execute(query, (username, password_hash))

        db.commit()

        print("Admin Account Created Successfully!")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        db.close()