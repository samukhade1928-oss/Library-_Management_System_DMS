from database import connect_db

db = connect_db()

if db:
    print("Library Management System Started Successfully!")

    db.close()