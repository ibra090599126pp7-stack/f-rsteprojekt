from flask import Flask, render_template, request, redirect
import sqlite3
import hashlib
import os

app = Flask(__name__)

def hash_password(adgangskode):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((adgangskode + salt).encode()).hexdigest()
    return hashed + ":" + salt

def check_password(gemt_adgangskode, indtastet_adgangskode):
    hashed, salt = gemt_adgangskode.split(":")
    tjek = hashlib.sha256((indtastet_adgangskode + salt).encode()).hexdigest()
    return tjek == hashed

def init_db():
    with sqlite3.connect("database.db") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS BRUGERE (
                id          INTEGER PRIMARY KEY,
                brugernavn  TEXT UNIQUE,
                adgangskode TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS PROFILER (
                id        INTEGER PRIMARY KEY,
                fornavn   TEXT,
                efternavn TEXT,
                email     TEXT UNIQUE,
                by        TEXT,
                telefon   TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS VAGT (
                id        INTEGER PRIMARY KEY,
                fornavn   TEXT,
                efternavn TEXT,
                dato      TEXT,
                starttid  TEXT,
                sluttid   TEXT
            )
        """)

init_db()

@app.route('/')
@app.route('/forside')
def home():
    return render_template('forside.html')

@app.route('/mad')
def mad():
    return render_template('mad.html')

@app.route('/om-os')
def om_os():
    return render_template('om-os.html')

@app.route('/MissionVision')
def mission_vision():
    return render_template('MissionVision.html')

@app.route('/verdensmaal')
def verdensmaal():
    return render_template('verdensmaal.html')

@app.route('/opret', methods=['GET', 'POST'])
def opret():
    if request.method == 'POST':
        brugernavn  = request.form['brugernavn']
        adgangskode = request.form['kode']
        fornavn     = request.form['fornavn']      # ændret fra navn
        efternavn   = request.form['efternavn']    # ny
        email       = request.form['email']
        by          = request.form['city']
        telefon     = request.form['phone']

        with sqlite3.connect("database.db") as db:
            db.execute(
                "INSERT INTO BRUGERE (brugernavn, adgangskode) VALUES (?,?)",
                (brugernavn, hash_password(adgangskode))
            )
            db.execute(
                "INSERT INTO PROFILER (fornavn, efternavn, email, by, telefon) VALUES (?,?,?,?,?)",
                (fornavn, efternavn, email, by, telefon)
            )

        return redirect('/login')
    return render_template('opret.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        brugernavn  = request.form['brugernavn']
        adgangskode = request.form['kode']

        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT adgangskode FROM BRUGERE WHERE brugernavn = ?",
                (brugernavn,)
            )
            række = cursor.fetchone()

        if række and check_password(række[0], adgangskode):
            if brugernavn == 'admin':
                return redirect('/database')
            return redirect(f'/kalender/{brugernavn}')  # send til kalender

        return "<h2>Forkert brugernavn eller adgangskode</h2><a href='/login'>Prøv igen</a>"

    return render_template('login_system.html')

@app.route('/kalender/<brugernavn>', methods=['GET', 'POST'])
def kalender(brugernavn):
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        # find id via brugernavn
        cursor.execute(
            "SELECT id FROM BRUGERE WHERE brugernavn = ?",
            (brugernavn,)
        )
        bruger_id = cursor.fetchone()[0]

        # brug samme id til at hente navn fra PROFILER
        cursor.execute(
            "SELECT fornavn, efternavn FROM PROFILER WHERE id = ?",
            (bruger_id,)
        )
        profil = cursor.fetchone()

    if request.method == 'POST':
        dato     = request.form['dato']
        starttid = request.form['starttid']
        sluttid  = request.form['sluttid']

        with sqlite3.connect("database.db") as db:
            db.execute(
                "INSERT INTO VAGT (fornavn, efternavn, dato, starttid, sluttid) VALUES (?,?,?,?,?)",
                (profil[0], profil[1], dato, starttid, sluttid)
            )

        return redirect(f'/kalender/{brugernavn}')

    return render_template('kalender.html', brugernavn=brugernavn, profil=profil)

@app.route('/database')
def database():
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM VAGT")
        vagter = cursor.fetchall()
    return render_template('database.html', vagter=vagter)

if __name__ == '__main__':
    app.run(debug=False)