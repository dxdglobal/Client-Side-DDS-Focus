def get_ai_filtered_projects(email, username):
    if not email and not username:
        return jsonify({"status": "error", "message": "No user info provided."}), 400

    db_host = "92.113.22.65"
    db_user = "u906714182_sqlrrefdvdv"
    db_password = "3@6*t:lU"
    db_name = "u906714182_sqlrrefdvdv"
    port = 3306

    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    try:
        # Query combining 4 sources
        query = f"""
            SELECT DISTINCT tblprojects.*, 'Project Creator / Task Creator / Member / Assigned' as source
            FROM tblprojects
            LEFT JOIN tblstaff ON tblprojects.addedfrom = tblstaff.staffid
            LEFT JOIN tblproject_members ON tblprojects.id = tblproject_members.project_id
            LEFT JOIN tbltasks ON tblprojects.id = tbltasks.rel_id AND tbltasks.rel_type = 'project'
            LEFT JOIN tbltask_assigned ON tbltasks.id = tbltask_assigned.taskid
            WHERE tblstaff.email = %s
               OR CONCAT(tblstaff.firstname, ' ', tblstaff.lastname) = %s
               OR tblproject_members.staff_id = tblstaff.staffid
               OR tbltasks.addedfrom = tblstaff.staffid
               OR tbltask_assigned.staff_id = tblstaff.staffid
        """

        results = veritabani.sorgu_calistir(query, (email, username))
        print(f"✅ Found {len(results)} projects without AI.")
        return jsonify({"status": "success", "projects": results})
    except Exception as e:
        print(f"❌ DB error in get_ai_filtered_projects (non-AI): {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
