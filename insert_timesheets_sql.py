import pymysql
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# DB credentials
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Dummy entries to insert
dummy_entries = [
    {
        "task_id": 900,
        "staff_id": 152,
        "start_time": "1714891000",
        "end_time": "1714891300",
        "hourly_rate": "55.00",
        "note": " Hamza Haseeb is testing Now jnb"
    },
    {
        "task_id": 901,
        "staff_id": 152,
        "start_time": "1714891400",
        "end_time": "1714891700",
        "hourly_rate": "60.00",
        "note": " Dummy entry AFTER test"
    }
]

# Insert into DB
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        for entry in dummy_entries:
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
            cursor.execute(query, params)
            print(f" Inserted dummy entry with task_id {entry['task_id']}")
        connection.commit()
finally:
    connection.close()

