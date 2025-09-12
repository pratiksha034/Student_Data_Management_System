
import pymysql
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",       
        password="pra@932214", 
        database="student_management",
        cursorclass=pymysql.cursors.DictCursor   
    )
