from flask import Flask, render_template, request, redirect, url_for, make_response
import pandas as pd
import pymysql
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from db_config import get_db_connection   # ✅ your DB connection file

app = Flask(__name__)

# ----------------------------
# Home Page - list all students
# ----------------------------
@app.route('/')
def home():   # 🔥 renamed from index() → home()
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students ORDER BY prn_number")
    students = cursor.fetchall()
    db.close()
    return render_template('index.html', students=students)


# ----------------------------
# Add Student
# ----------------------------
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
        return redirect(url_for('home'))   # 🔥 redirect to home
    return render_template('add_student.html')


# ----------------------------
# Find Student
# ----------------------------
@app.route('/find', methods=['GET', 'POST'])
def find_student():
    students = []
    if request.method == 'POST':
        search_column = request.form.get("search_column")
        search_value = request.form.get("search_value")

        if search_column and search_value:
            db = get_db_connection()
            cursor = db.cursor()

            query = f"SELECT * FROM students WHERE {search_column} LIKE %s"
            
            if search_column in ["prn_number", "branch_code", "contact_number", "percentage", "scholarship_eligible"]:
                query = f"SELECT * FROM students WHERE {search_column} = %s"
                cursor.execute(query, (search_value,))
            else:
                cursor.execute(query, ("%" + search_value + "%",))

            students = cursor.fetchall()
            db.close()

    return render_template("find_student.html", students=students)


# ----------------------------
# Export CSV
# ----------------------------
@app.route('/export/csv')
def export_csv():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    db.close()

    df = pd.DataFrame(rows)   # ✅ directly from dict rows
    response = make_response(df.to_csv(index=False))
    response.headers["Content-Disposition"] = "attachment; filename=students.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


# ----------------------------
# Export Excel
# ----------------------------
@app.route('/export/excel')
def export_excel():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    db.close()

    df = pd.DataFrame(rows)   # ✅ directly from dict rows

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=students.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


# ----------------------------
# Export PDF
# ----------------------------
@app.route('/export/pdf')
def export_pdf():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    db.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    style = getSampleStyleSheet()

    # ✅ Build table with dict keys
    if rows:
        data = [list(rows[0].keys())]   # headers
        for r in rows:
            data.append(list(r.values()))
    else:
        data = [["No data found"]]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(Paragraph("Student Report", style["Heading1"]))
    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Disposition"] = "attachment; filename=students.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response



# ----------------------------
# Run Flask App
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
