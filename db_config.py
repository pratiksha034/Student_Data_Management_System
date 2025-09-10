import pymysql

def get_db_connection():
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="pra@932214",  # 🔹 change to your MySQL password
        database="student_management",
        cursorclass=pymysql.cursors.DictCursor
    )
    return db

