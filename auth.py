import hashlib
import os

from database import connect_db


def hash_password(password, salt=None):

    if salt is None:
        salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        200000
    )

    return salt.hex() + "$" + password_hash.hex()


def verify_password(password, stored_hash):

    try:
        salt_hex, original_hash = stored_hash.split("$")

        salt = bytes.fromhex(salt_hex)

        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            200000
        )

        return new_hash.hex() == original_hash

    except ValueError:
        return False


def login_admin(username, password):

    db = connect_db()

    if db is None:
        return False

    try:
        cursor = db.cursor()

        query = """
        SELECT password_hash
        FROM admin
        WHERE username = %s
        """

        cursor.execute(query, (username,))

        result = cursor.fetchone()

        if result and verify_password(password, result[0]):
            return True

        return False

    finally:
        cursor.close()
        db.close()