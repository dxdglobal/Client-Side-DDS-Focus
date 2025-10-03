from moduller.veritabani_yoneticisi import VeritabaniYoneticisi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# DB config
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Connect to DB
db = VeritabaniYoneticisi(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
db.baglanti_olustur()

# Dummy data with staff_id = 146 and note = "Hamza is testing"
dummy_entries = [
    {
        "task_id": 1087,
        "staff_id": 146,
        "start_time": "2025-05-01 09:00:00",
        "end_time": "2025-05-01 11:00:00",
        "hourly_rate": "2.50",
        "note": "Hamza is testing"
    },
    {
        "task_id": 1087,
        "staff_id": 146,
        "start_time": "2025-05-01 14:00:00",
        "end_time": "2025-05-01 15:30:00",
        "hourly_rate": "3.00",
        "note": "Hamza is testing"
    }
]

# Insert dummy records
for entry in dummy_entries:
    try:
        query = """
            INSERT INTO tbltaskstimers (task_id, staff_id, start_time, end_time, note, hourly_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            entry["task_id"],
            entry["staff_id"],
            entry["start_time"],
            entry["end_time"],
            entry["note"],
            entry["hourly_rate"]
        )
        db.sorgu_calistir(query, params)
        print(f" Inserted dummy entry for task {entry['task_id']}")
    except Exception as e:
        print(f" Error inserting dummy entry: {e}")

#  Verify inserted rows
print("\n Verifying inserted data for Hamza:")
try:
    rows = db.sorgu_calistir("""
        SELECT id, task_id, staff_id, start_time, end_time, hourly_rate, note
        FROM tbltaskstimers
        WHERE staff_id = 146 AND note = 'Hamza is testing'
        ORDER BY id DESC
        LIMIT 10
    """)
    if rows:
        for row in rows:
            print(row)
    else:
        print(" No matching records found.")
except Exception as e:
    print(f" Error during verification: {e}")

