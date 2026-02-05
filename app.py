from flask import Flask, request, jsonify, render_template
import sqlite3
from model import detect_fraud   # Ton modèle de détection

app = Flask(__name__)

DB_PATH = "database.db"


# ---------- Connexion DB ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Création table ----------
def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                email TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()


# On initialise la DB au démarrage de l'app
init_db()


# ---------- Routes ----------
@app.route("/login")
def login():
    return render_template("login.html")  # ton formulaire EXISTANT


@app.route("/")
def home():
    # index.html doit être dans le dossier "templates/"
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit_transaction():
    # On récupère le JSON envoyé par le front
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Requête JSON invalide ou vide"}), 400

    # Récupération des champs avec valeurs par défaut None
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    contact = data.get("contact")
    email = data.get("email")

    # Validation minimale côté backend
    missing = [field for field, value in {
        "first_name": first_name,
        "last_name": last_name,
        "contact": contact,
        "email": email,
    }.items() if not value]

    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    # Détection fraude (à adapter à ton modèle)
    status = detect_fraud(contact, email)

    # Sauvegarde DB
    with get_db() as db:
        db.execute("""
            INSERT INTO transactions (first_name, last_name, contact, email, status)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, contact, email, status))
        db.commit()

        print("✅ Transaction insérée :", first_name, last_name, email, status)

    return jsonify({"status": status})


@app.route("/all")
def all_transactions():
    with get_db() as db:
        rows = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
        return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    # debug=True pour développement uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
    # tracted by git