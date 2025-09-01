from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define the token and API URL
CRM_API_URL = "https://crm.deluxebilisim.com/api/projects/search/"
CRM_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGVsdXhldGltZSIsIm5hbWUiOiJkZWx1eGV0aW1lIiwiQVBJX1RJTUUiOjE3NDUzNDQyNjJ9.kJGo5DksaPwkHwufDvLMGaMmjk5q2F7GhjzwdHtfT_o"

# Route to handle fetching projects
@app.route('/get_projects/<staffid>', methods=['GET'])
def get_projects(staffid):
    try:
        # Send a GET request to the CRM API with the staffid
        response = requests.get(f"{CRM_API_URL}{staffid}", headers={
            'Authorization': f'Bearer {CRM_API_TOKEN}',
            'Content-Type': 'application/json'
        })
        
        # If the request was successful, log the response data to the console
        if response.status_code == 200:
            projects = response.json()
            print("Projects fetched:", projects)  # Console log the projects data
            return jsonify(projects)
        else:
            print(f"Error fetching projects, status code: {response.status_code}")  # Log the error in case of failure
            return jsonify({"error": "Failed to fetch projects"}), response.status_code

    except Exception as e:
        print("Error during request:", str(e))  # Log the exception
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

