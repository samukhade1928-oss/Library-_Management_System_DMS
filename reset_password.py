from database import connect_db
from auth import hash_password
from getpass import getpass

username = "SAMUKHADE"

print("===== ADMIN PASSWORD RESET =====")

new_password = getpass("Enter New Password: ")
confirm_password = getpass("Confirm New Password: ")

if not new_password:
    print("Password cannot be empty.")

elif new_password != confirm_password:
    print("Passwords do not match.")

else:
    db = connect_db()

    if db:
        cursor = db.cursor()

        try:
            new_hash = hash_password(new_password)

            query = """
            UPDATE admin
            SET password_hash = %s
            WHERE username = %s
            """

            cursor.execute(query, (new_hash, username))
            db.commit()

            if cursor.rowcount == 1:
                print("Password Reset Successfully!")
            else:
                print("Admin username not found.")

        except Exception as e:
            db.rollback()
            print("Error:", e)

        finally:
            cursor.close()
            db.close()