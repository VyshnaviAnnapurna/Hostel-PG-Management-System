from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "admin_secret_key"

# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect("hostel.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- ADMIN LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")
        else:
            return "Wrong Credentials"
    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM rooms")
    rooms_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students")
    students_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM payments")
    payments_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints")
    complaints_count = cur.fetchone()[0]

    con.close()

    return render_template(
        "admin_dashboard.html",
        rooms_count=rooms_count,
        students_count=students_count,
        payments_count=payments_count,
        complaints_count=complaints_count
    )

# ---------------- ROOMS ----------------
@app.route("/rooms", methods=["GET", "POST"])
def rooms():
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        room_no = request.form["room_no"]
        capacity = request.form["capacity"]
        cur.execute(
            "INSERT INTO rooms (room_no, capacity, occupied) VALUES (?, ?, 0)",
            (room_no, capacity)
        )
        con.commit()

    cur.execute("SELECT * FROM rooms")
    rooms = cur.fetchall()
    con.close()

    return render_template("rooms.html", rooms=rooms)

@app.route("/delete_room/<int:room_id>", methods=["POST"])
def delete_room(room_id):
    con = get_db()
    con.execute("DELETE FROM rooms WHERE id=?", (room_id,))
    con.commit()
    con.close()
    return redirect("/rooms")

# ---------------- STUDENTS ----------------
@app.route("/students", methods=["GET", "POST"])
def students():
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        room_id = request.form["room_id"]

        cur.execute(
            "INSERT INTO students (name, email, password, room_id) VALUES (?, ?, ?, ?)",
            (name, email, password, room_id)
        )

        cur.execute(
            "UPDATE rooms SET occupied = occupied + 1 WHERE id=?",
            (room_id,)
        )
        con.commit()

    cur.execute("""
        SELECT students.id, students.name, students.email, rooms.room_no
        FROM students
        LEFT JOIN rooms ON students.room_id = rooms.id
    """)
    students = cur.fetchall()

    cur.execute("SELECT id, room_no FROM rooms WHERE occupied < capacity")
    rooms = cur.fetchall()

    con.close()
    return render_template("students.html", students=students, rooms=rooms)

@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    con = get_db()
    con.execute("DELETE FROM students WHERE id=?", (student_id,))
    con.commit()
    con.close()
    return redirect("/students")

# ---------------- PAYMENTS ----------------
@app.route("/payments", methods=["GET", "POST"])
def payments():
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        student_id = request.form["student_id"]
        amount = request.form["amount"]
        date = request.form["date"]

        cur.execute(
            "INSERT INTO payments (student_id, amount, payment_date) VALUES (?, ?, ?)",
            (student_id, amount, date)
        )
        con.commit()

    cur.execute("""
        SELECT students.name, payments.amount, payments.payment_date
        FROM payments
        JOIN students ON payments.student_id = students.id
    """)
    payments = cur.fetchall()

    cur.execute("SELECT id, name FROM students")
    students = cur.fetchall()

    con.close()
    return render_template("payments.html", payments=payments, students=students)

# ---------------- COMPLAINTS ----------------
@app.route("/complaints")
def admin_complaints():
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT complaints.id, students.name, complaints.subject,
               complaints.complaint, complaints.status
        FROM complaints
        JOIN students ON complaints.student_id = students.id
    """)
    complaints = cur.fetchall()

    con.close()
    return render_template("admin_complaints.html", complaints=complaints)

@app.route("/resolve_complaint/<int:id>")
def resolve(id):
    if "admin" not in session:
        return redirect("/login")

    con = get_db()
    con.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/complaints")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- STUDENT LOGIN ----------------
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM students WHERE email=? AND password=?",
            (email, password)
        )
        student = cur.fetchone()
        con.close()

        if student:
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            return redirect("/student_dashboard")
        else:
            return "Invalid Login"

    return render_template("student_login.html")

# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student_dashboard")
def student_dashboard():
    if "student_id" not in session:
        return redirect("/student_login")

    student_id = session["student_id"]
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM complaints WHERE student_id=?", (student_id,))
    total_complaints = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM complaints WHERE student_id=? AND status='Resolved'",
        (student_id,)
    )
    resolved_complaints = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM payments WHERE student_id=?", (student_id,))
    payment_count = cur.fetchone()[0]

    con.close()

    return render_template(
        "student_dashboard.html",
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        payment_count=payment_count,
        student_name=session["student_name"]
    )

# ---------------- STUDENT COMPLAINTS ----------------
@app.route("/view_complaints")
def view_complaint():
    if "student_id" not in session:
        return redirect("/student_login")

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "SELECT subject, complaint, status, created_at FROM complaints WHERE student_id=?",
        (session["student_id"],)
    )
    complaints = cur.fetchall()
    con.close()

    return render_template("view_complaints.html", complaints=complaints)

@app.route("/student_complaint", methods=["GET", "POST"])
def student_complaint():
    if "student_id" not in session:
        return redirect("/student_login")

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        subject = request.form["subject"]
        complaint = request.form["complaint"]

        cur.execute(
            "INSERT INTO complaints (student_id, subject, complaint, status) VALUES (?, ?, ?, 'Pending')",
            (session["student_id"], subject, complaint)
        )
        con.commit()
        con.close()
        return redirect("/view_complaints")

    return render_template("student_complaint.html")

# ---------------- STUDENT PAYMENTS ----------------
@app.route("/student_payments")
def student_payments():
    if "student_id" not in session:
        return redirect("/student_login")

    con = get_db()
    cur = con.cursor()
    cur.execute(
        "SELECT amount, payment_date FROM payments WHERE student_id=?",
        (session["student_id"],)
    )
    payments = cur.fetchall()
    con.close()

    return render_template("student_payments.html", payments=payments)

@app.route("/student_logout")
def student_logout():
    session.clear()
    return redirect("/student_login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
