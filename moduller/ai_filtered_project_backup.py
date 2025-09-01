
import openai
import os
from flask import jsonify
from moduller.veritabani_yoneticisi import VeritabaniYoneticisi

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You generate only clean executable SQL SELECT queries based on strict real database rules."},
            {"role": "user", "content": prompt}
        ]
    )
    sql_query = response['choices'][0]['message']['content'].strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    if not sql_query.lower().startswith("select"):
        raise ValueError("Returned SQL is invalid")
    return sql_query

def execute_sql(sql_query, veritabani):
    try:
        return veritabani.sorgu_calistir(sql_query)
    except Exception as e:
        print(f" SQL error: {str(e)}")
        return []

def get_ai_filtered_projects(email, username):
    if not email and not username:
        return jsonify({"status": "error", "message": "No user info provided."}), 400

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    port = int(os.getenv("DB_PORT"))

    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    base_instructions = f"""
    Database structure rules:

    - tblstaff:
      - Email: tblstaff.email
      - Full name: CONCAT(tblstaff.firstname, ' ', tblstaff.lastname)

    - tblprojects:
      - ID: tblprojects.id
      - Created by: tblprojects.addedfrom (staffid)

    - tblproject_members:
      - project_id = tblprojects.id
      - staff_id = tblstaff.staffid

    - tbltasks:
      - rel_type = 'project'
      - rel_id = tblprojects.id
      - addedfrom = tblstaff.staffid

    - tbltask_assigned:
      - taskid links to tbltasks.id
      - staff_id = tblstaff.staffid

    Match staff strictly by:
    - tblstaff.email = '{email}'
    - OR CONCAT(tblstaff.firstname, ' ', tblstaff.lastname) = '{username}'
    - NO markdown, NO explanation.
    - Only return executable SQL SELECT tblprojects.* queries.
    """

    prompts = [
        base_instructions + "Find projects created by the staff (tblprojects.addedfrom = tblstaff.staffid).",
        base_instructions + "Find projects where the staff created tasks (tbltasks.addedfrom) with tbltasks.rel_type = 'project'.",
        base_instructions + "Find projects where the staff is a project member (tblproject_members.staff_id).",
        base_instructions + "Find projects where the staff is assigned to tasks linked to the project (tbltask_assigned)."
    ]

    source_mapping = {
        0: "Project Creator",
        1: "Task Creator",
        2: "Project Member",
        3: "Task Assigned"
    }

    all_results = []
    seen_project_ids = set()

    for i, prompt in enumerate(prompts):
        print(f" Trying strict smart search method {i+1}...")
        try:
            sql_query = ask_openai(prompt)
            print(f" Generated SQL:\n{sql_query}")
            results = execute_sql(sql_query, veritabani)
            for project in results:
                pid = project.get("id")
                if pid and pid not in seen_project_ids:
                    seen_project_ids.add(pid)
                    project["source"] = source_mapping.get(i, f"Method {i+1}")
                    all_results.append(project)
        except Exception as e:
            print(f"Skipping method {i+1} due to error: {str(e)}")

    if all_results:
        print(f" Total strict unique projects found: {len(all_results)}")
        return jsonify({"status": "success", "projects": all_results})
    else:
        print(" No related projects found after strict methods.")
        return jsonify({"status": "success", "projects": []})

