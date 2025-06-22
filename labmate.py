import sqlite3
import csv
import re

DB_NAME = "labplanner.db"

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            user TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    conn.commit()
    return conn, c

def add_experiment(c, conn):
    name = input("Experimentnaam: ")
    while True:
        date = input("Datum (YYYY-MM-DD): ")
        if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", date):
            break
        else:
            print("Format klopt niet")
    while True:
        start_time = input("Starttijd (HH:MM): ")
        if start_time == "":
            print("Format klopt niet")
        else:
            break 
    duration = int(input("Duur in minuten: "))
    user = input("Gebruiker: ")

    c.execute('''
        INSERT INTO experiments (name, date, start_time, duration, user)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, date, start_time, duration, user))
    conn.commit()
    print("Experiment toegevoegd!\n")

def list_experiments(c):
    c.execute("SELECT * FROM experiments")
    rows = c.fetchall()
    if not rows:
        print("Geen experimenten gevonden.\n")
        return
    print(f"{'ID':<3} {'Naam':<20} {'Datum':<10} {'Start':<6} {'Duur':<5} {'Gebr.':<10} {'Status':<10}")
    for row in rows:
        print(f"{row[0]:<3} {row[1]:<20} {row[2]:<10} {row[3]:<6} {row[4]:<5} {row[5]:<10} {row[8]:<10}")
    print()


def mark_done(c, conn):
    list_experiments(c)
    exp_id = input("ID van experiment om af te ronden: ")
    c.execute("UPDATE experiments SET status='done' WHERE id=?", (exp_id,))
    conn.commit()
    print(f"Experiment {exp_id} gemarkeerd als afgerond.\n")


def delete_experiment(c, conn):
    list_experiments(c)
    exp_id = input("ID van experiment om te verwijderen: ")
    c.execute("DELETE FROM experiments WHERE id=?", (exp_id,))
    conn.commit()
    print(f"Experiment {exp_id} verwijderd.\n")


def export_csv(c):
    c.execute("SELECT * FROM experiments")
    rows = c.fetchall()
    with open('experiments_export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID','Naam','Datum','Starttijd','Duur','Gebruiker','Materialen','Locatie','Status'])
        writer.writerows(rows)
    print("Data geëxporteerd naar experiments_export.csv\n")

def calculate_tm(sequence):
    sequence = sequence.upper()
    if not re.fullmatch(r"[ATGC]+", sequence):
        return("Fout: de sequentie mag alleen A, T, G en C bevatten.")
    a = sequence.count("A")
    t = sequence.count("T")
    g = sequence.count("G")
    c = sequence.count("C")
    tm = 2 * (a + t) + 4 * (g + c)
    return(f"Geschatte smelttemperatuur: {tm}°C\n")