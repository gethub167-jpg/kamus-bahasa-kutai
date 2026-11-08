from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "kamus.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET"])
def index():
    kata = request.args.get("q", "").strip()
    hasil = []

    if kata:
        pola = f"%{kata}%"

        conn = get_db()

        try:
            hasil = conn.execute("""
                SELECT *
                FROM kamus
                WHERE kata_kutai LIKE ?
                   OR kata_turunan LIKE ?
                   OR arti_indonesia LIKE ?
                   OR contoh_kalimat LIKE ?
                   OR terjemahan_contoh LIKE ?
                ORDER BY
                    CASE
                        WHEN LOWER(TRIM(kata_kutai)) = LOWER(?) THEN 1
                        WHEN LOWER(TRIM(kata_turunan)) = LOWER(?) THEN 2
                        WHEN LOWER(TRIM(arti_indonesia)) = LOWER(?) THEN 3
                        ELSE 4
                    END,
                    kata_kutai
                LIMIT 50
            """, (
                pola,
                pola,
                pola,
                pola,
                pola,
                kata,
                kata,
                kata
            )).fetchall()

        finally:
            conn.close()

    return render_template(
        "index.html",
        kata=kata,
        hasil=hasil
    )


if __name__ == "__main__":
    app.run(debug=True)