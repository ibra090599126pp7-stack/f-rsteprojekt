from flask import Flask, render_template, request, redirect
import sqlite3
import hashlib
import os  # Til at generere et tilfældigt salt

app = Flask(__name__)

def hash_password(adgangskode):
    salt = os.urandom(16).hex()  # Lav et tilfældigt salt
    hashed = hashlib.sha256((adgangskode + salt).encode()).hexdigest()
    return hashed + ":" + salt  # Gem begge dele sammen

def check_password(gemt_adgangskode, indtastet_adgangskode):
    hashed, salt = gemt_adgangskode.split(":")  # Adskil hash og salt
    tjek = hashlib.sha256((indtastet_adgangskode + salt).encode()).hexdigest()
    return tjek == hashed  # Sammenlign


@app.route('/')
def home():
    return render_template('forside.html')

@app.route('/forside')
def Forside():
    return render_template('forside.html')

@app.route('/login')
def login():
    return render_template('login.html')

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


def init_db():
    with sqlite3.connect("database.db") as db:
        db.execute("CREATE TABLE IF NOT EXISTS BRUGERE (id INTEGER PRIMARY KEY, brugernavn TEXT, adgangskode TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS PROFILER (id INTEGER PRIMARY KEY, navn TEXT, email TEXT, by TEXT, telefon TEXT)")

init_db()


@app.route('/opret', methods=['GET', 'POST'])
def opret():
    if request.method == 'POST':
        brugernavn = request.form['brugernavn']
        adgangskode = hash_password(request.form['kode'])  # Hash adgangskoden
        navn = request.form['navn']
        email = request.form['email']
        by = request.form['city']
        telefon = request.form['phone']

        with sqlite3.connect("database.db") as db:
            db.execute("INSERT INTO BRUGERE (brugernavn, adgangskode) VALUES (?,?)", (brugernavn, adgangskode))
            db.execute("INSERT INTO PROFILER (navn, email, by, telefon) VALUES (?,?,?,?)", (navn, email, by, telefon))

        return redirect('/login_system')
    else:
        return render_template('opret.html')


@app.route('/login_system', methods=['GET', 'POST'])
def login_system():
    if request.method == 'POST':
        brugernavn = request.form['brugernavn']
        adgangskode = request.form['kode']

        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM BRUGERE WHERE brugernavn=?", (brugernavn,))
            bruger = cursor.fetchone()

        if bruger and check_password(bruger[2], adgangskode):  # Tjek password
            return render_template("login.html")
        else:
            return "<h2>Forkert brugernavn eller adgangskode</h2><a href='/login_system'>Prøv igen</a>"
    else:
        return render_template('login_system.html')


if __name__ == '__main__':
    app.run(debug=True)