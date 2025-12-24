import sqlite3, os

db_path = os.path.join(r"C:\www\A2_Recipe_App\src", "db.sqlite3")
print("DB:", db_path, "exists:", os.path.exists(db_path))
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cur.fetchall()]
print("Tables found:")
for t in tables:
    print("-", t)
conn.close()
