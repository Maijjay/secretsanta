import sqlite3
from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

def init_db():
    db = sqlite3.connect("database.db")
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, used INTEGER DEFAULT 0)")
    db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, message TEXT)")
    db.execute ("CREATE TABLE IF NOT EXISTS replies (id INTEGER PRIMARY KEY, message_id INTEGER, reply TEXT, FOREIGN KEY(message_id) REFERENCES messages(id))")
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # You can insert the users here you wish to be in the raffle
    if count == 0:
        db.executemany(
            "INSERT INTO users (name) VALUES (?)",
            [("Maija",), ("Nico",), ("Paula",),  ("Janne",), ("Elina",), ("Mervi",), ("Juha",), ("Pekka",), ("Emma",), ("Sirkka",)]
        )
        db.commit()

    db.close()

@app.route("/draw-secret-santa", methods=["POST"])
def draw_secret_santa():
    db = sqlite3.connect("database.db")

    user = request.form["user"]

    # Pick unused users except yourself
    unused = db.execute(
        "SELECT id, name FROM users WHERE used = 0 AND name != ?",
        (user,)
    ).fetchall()

    if not unused:
        db.close()
        names, messages = load_index_data()
        return render_template("index.html", santa=None, names=names, messages=messages)

    chosen = random.choice(unused)

    db.execute("UPDATE users SET used = 1 WHERE id = ?", (chosen[0],))
    db.commit()
    db.close()

    names, messages = load_index_data()
    return render_template("index.html", santa=chosen[1], names=names, messages=messages)


@app.route("/send", methods=["POST"])
def send():
    content = request.form["message"]
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO messages (message) VALUES (?)", [content])
    db.commit()
    db.close()
    return redirect("/")  

@app.route("/reply", methods=["POST"])
def reply():
    message_id = request.form["message_id"]
    reply = request.form["reply"]
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO replies (message_id, reply) VALUES (?, ?)", (message_id, reply))
    db.commit()
    db.close()
    return redirect("/")

def load_index_data():
    db = sqlite3.connect("database.db")

    names = db.execute("SELECT name FROM users").fetchall()

    message_rows = db.execute("SELECT id, message FROM messages").fetchall()

    messages = []
    for msg_id, msg_text in message_rows:
        reply_rows = db.execute("SELECT reply FROM replies WHERE message_id = ?", (msg_id,)).fetchall()
        replies = [r[0] for r in reply_rows]
        messages.append((msg_id, msg_text, replies))

    db.close()
    return names, messages


@app.route("/", methods=["GET"])
def index():
    names, messages = load_index_data()
    return render_template("index.html", names=names, messages=messages, santa=None)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
