from flask import Flask, render_template, request, redirect, url_for
import pymysql
from db_config import get_db_connection

app = Flask(__name__)

# Home Page - list all students
@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students ORDER BY prn_number")
    students = cursor.fetchall()
    db.close()
    return render_template('index.html', students=students)

# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        data = request.form
        db = get_db_connection()
        cursor = db.cursor()
        sql = """INSERT INTO students 
                 (prn_number, name, contact_number, dob, admission_date, branch_code, percentage, scholarship_eligible, scholarship_category, city)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (
            data['prn'], data['name'], data['contact'], data['dob'], 
            data['admission_date'], data['branch'], data['percentage'], 
            int(data.get('scholarship', 0)), data.get('category'), data['city']
        )
        cursor.execute(sql, values)
        db.commit()
        db.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Find Student by Name
@app.route('/find', methods=['GET', 'POST'])
def find_student():
    students = []
    if request.method == 'POST':
        search_column = request.form.get("search_column")
        search_value = request.form.get("search_value")

        if search_column and search_value:
            db = get_db_connection()
            cursor = db.cursor()

            # Build query dynamically
            query = f"SELECT * FROM students WHERE {search_column} LIKE %s"
            
            # Exact match for PRN, branch_code, contact_number, percentage, scholarship_eligible
            if search_column in ["prn_number", "branch_code", "contact_number", "percentage", "scholarship_eligible"]:
                query = f"SELECT * FROM students WHERE {search_column} = %s"
                cursor.execute(query, (search_value,))
            else:
                cursor.execute(query, ("%" + search_value + "%",))

            students = cursor.fetchall()
            db.close()

    return render_template("find_student.html", students=students)




if __name__ == '__main__':
    app.run(debug=True)
