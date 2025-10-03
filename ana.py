from moduller.veritabani_yoneticisi import VeritabaniYoneticisi
import os
from dotenv import load_dotenv

def ana():
    """
    Main execution pipeline for database connection.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Database config from .env file
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    port = int(os.getenv("DB_PORT"))

    print("[INFO] Attempting to connect to the MySQL database...")

    # Connect to the database
    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    # Check if the connection is active
    if not veritabani.baglanti_testi():
        print("[ERROR]  Database connection failed. ana")
        return

    print("[INFO]  Database connection successful.")

    # Close the database connection after use
    veritabani.kapat()
    print("[INFO] MySQL connection closed.")

if __name__ == "__main__":
    ana()

