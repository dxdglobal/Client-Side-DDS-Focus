import os
import mysql.connector
import openai
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# --- Database Helper ---
class VeritabaniYoneticisi:
    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def baglanti_olustur(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

    def tablo_listele(self):
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def kolonlari_getir(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return columns

# --- OpenAI Helper ---
def ask_openai_table_analysis(table_name, columns):
    prompt = f"""
You are a MySQL schema expert.

I need to find a table suitable for storing **user timesheet entries**, with fields like:
- member or user or employee
- start_time or check_in or clock_in
- end_time or check_out or clock_out
- time_spent or duration or total_time

Here is a table:
- Name: {table_name}
- Columns: {columns}

Is this table suitable? 
If yes, reply ONLY: YES: <table_name>. 
If not, reply ONLY: NO.
No explanations, no markdown.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You only return YES or NO about table suitability, no explanation."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# --- Main Smart Finder ---
def find_timesheet_table():
    print(" Starting Smart AI Table Finder...")

    db = VeritabaniYoneticisi(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
    try:
        db.baglanti_olustur()
    except Exception as e:
        print(f" Database Connection Error: {str(e)}")
        return

    tables = db.tablo_listele()
    if not tables:
        print(" No tables found in database.")
        return

    print(f" Found {len(tables)} tables. Analyzing...")

    for i, table in enumerate(tables):
        try:
            columns = db.kolonlari_getir(table)
            print(f" Checking table ({i+1}/{len(tables)}): {table} Columns: {columns}")
            ai_response = ask_openai_table_analysis(table, columns)
            print(f" AI Response: {ai_response}")

            if ai_response.startswith("YES:"):
                final_table = ai_response.split("YES:")[1].strip()
                print(f"\n Final Selected Timesheet Table: {final_table}")
                return final_table
        except Exception as e:
            print(f" Skipping table {table} due to error: {str(e)}")

    print(" No suitable table found after AI analysis.")
    return None

# --- Script Runner ---
if __name__ == "__main__":
    selected_table = find_timesheet_table()
    input("\n Finished. Press ENTER to exit...")

