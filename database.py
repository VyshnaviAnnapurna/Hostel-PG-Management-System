import sqlite3

DB_NAME = "hostel.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    con = get_db()
    cur = con.cursor()

    # ---------- ADMIN TABLE ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ---------- ROOMS TABLE ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_no TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        occupied INTEGER DEFAULT 0
    )
    """)

    # ---------- STUDENTS TABLE ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        room_id INTEGER,
        FOREIGN KEY (room_id) REFERENCES rooms(id)
    )
    """)

    # ---------- PAYMENTS TABLE ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        payment_date TEXT NOT NULL,
        status TEXT DEFAULT 'Paid',
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    # ---------- COMPLAINTS TABLE ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        complaint TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)

    con.commit()
    con.close()
    print("✅ Database and tables created successfully!")

if __name__ == "__main__":
    init_db()
