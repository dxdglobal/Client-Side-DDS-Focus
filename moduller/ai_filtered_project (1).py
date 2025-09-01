
import openai
import os
from flask import jsonify
from moduller.veritabani_yoneticisi import VeritabaniYoneticisi

# Setup OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_filtered_projects(email, username):
    """AI-based filter to get projects for provided email/username."""
    if not email and not username:
        return jsonify({"status": "error", "message": "No user info provided."}), 401

    # AI prompt to generate SQL
    filter_input = f"Get projects where staff is assigned using email '{email}'"
    prompt = f"""
    You are a SQL generator. Convert the user's request into a SELECT query for the Perfex CRM database.
    Only use safe and relevant fields. Focus on the `tblprojects` and `tblstaff` relationship.
    ---
    Request: {filter_input}
    Return SQL only.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that generates MySQL queries for a CRM database."},
                {"role": "user", "content": prompt}
            ]
        )
        sql_query = response['choices'][0]['message']['content'].strip()
        print(f" AI-generated SQL:\n{sql_query}")

    except Exception as e:
        return jsonify({"status": "error", "message": f"OpenAI error: {str(e)}"}), 500

    # Connect to the database
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    port = int(os.getenv("DB_PORT"))

    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    try:
        results = veritabani.sorgu_calistir(sql_query)
        print(f" Total AI-filtered projects: {len(results)}")
        return jsonify({"status": "success", "projects": results})
    except Exception as e:
        print(f" SQL Execution Failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e), "query": sql_query}), 500

