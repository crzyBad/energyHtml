from flask import Flask, render_template, url_for, redirect, session, request
import sys
import os.path
import sqlite3

db = "database.db"






# Pages #
app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/energy')
def energy():
    return render_template("energy.html")


@app.route('/electricVehicles')
def electricVehicles():
    return render_template("electricVehicles.html")


@app.route('/heatPumps')
def heatPumps():
    return render_template("heatPumps.html")


@app.route('/solarBattery')
def solarBattery():
    return render_template("solarBattery.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO user (name, email, password)
                VALUES (?, ?, ?);
            """, (name, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already in use", 400
        return redirect(url_for("logIn"))
    return render_template("register.html")



@app.route('/logIn', methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM user WHERE email=? AND password=?
        """, (email, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401

    return render_template("logIn.html")


# Log out
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/booking', methods=['GET', 'POST'])
def booking():

    if 'email' not in session:
        return redirect(url_for('logIn'))

    if request.method == "POST":
        date = request.form.get("date")
        bookingType = request.form.get("bookingType")
        email = session['email']

        if not bookingType:
            return render_template(
                "booking.html",
                error="Please select a booking type."
            )

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookings (email, date, bookingType)
            VALUES (?, ?, ?)
        """, (email, date, bookingType))

        conn.commit()
        conn.close()

        return redirect(url_for('bookings'))

    return render_template("booking.html")




@app.route('/bookings')
def bookings():
    if 'email' not in session:
        return redirect(url_for('logIn'))

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, bookingType
        FROM bookings
        WHERE email = ?
        ORDER BY date
    """, (session['email'],))

    user_bookings = cursor.fetchall()
    conn.close()

    return render_template("bookings.html", bookings=user_bookings)











# User table #
conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute ("""
CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password TEXT NOT NULL)
                """)


    # Bookings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    date TEXT NOT NULL,
    bookingType TEXT NOT NULL
);
""")



if __name__ == "__main__":
    app.run(debug=True)