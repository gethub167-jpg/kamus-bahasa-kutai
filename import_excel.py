import pandas as pd
import sqlite3
from pathlib import Path

# Lokasi project
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "data" / "Kamus_Bahasa_Kutai_Skala_Besar.xlsx"
DB_FILE = BASE_DIR / "kamus.db"

# Periksa file Excel
if not EXCEL_FILE.exists():
    raise FileNotFoundError(f"Excel tidak ditemukan: {EXCEL_FILE}")

print("Membaca file Excel...")

# Baca Excel
df = pd.read_excel(EXCEL_FILE, engine="openpyxl")

# Bersihkan nama kolom
df.columns = df.columns.str.strip()

# Kolom Excel
kolom = [
    "Kata Kutai",
    "Kata Turunan",
    "Arti Indonesia",
    "Contoh Kalimat Kutai",
    "Terjemahan Contoh"
]

# Periksa kelengkapan kolom
for nama in kolom:
    if nama not in df.columns:
        raise ValueError(f"Kolom tidak ditemukan: {nama}")

# Ambil kolom yang diperlukan
df = df[kolom].fillna("")

# Ganti nama kolom agar sesuai database
df.columns = [
    "kata_kutai",
    "kata_turunan",
    "arti_indonesia",
    "contoh_kalimat",
    "terjemahan_contoh"
]

# Hubungkan database
conn = sqlite3.connect(DB_FILE)

try:
    # Hapus tabel lama agar struktur tidak bentrok
    conn.execute("DROP TABLE IF EXISTS kamus")

    # Buat tabel baru
    conn.execute("""
        CREATE TABLE kamus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kata_kutai TEXT,
            kata_turunan TEXT,
            arti_indonesia TEXT,
            contoh_kalimat TEXT,
            terjemahan_contoh TEXT
        )
    """)

    # Masukkan data Excel
    df.to_sql(
        "kamus",
        conn,
        if_exists="append",
        index=False
    )

    # Index untuk pencarian
    conn.execute("""
        CREATE INDEX idx_kata_kutai
        ON kamus(kata_kutai)
    """)

    conn.execute("""
        CREATE INDEX idx_arti_indonesia
        ON kamus(arti_indonesia)
    """)

    conn.commit()

    # Hitung jumlah data
    jumlah = conn.execute(
        "SELECT COUNT(*) FROM kamus"
    ).fetchone()[0]

    print("--------------------------------")
    print("DATABASE BERHASIL DIBUAT!")
    print(f"Jumlah kosakata: {jumlah}")
    print(f"Lokasi database: {DB_FILE}")
    print("--------------------------------")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()