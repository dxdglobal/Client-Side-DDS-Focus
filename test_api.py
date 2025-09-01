import requests
import json

# ✅ API ka URL jahan data bhejna hai
url = "https://dxdtime.ddsolutions.io/en/api/update-log-info"

# ✅ Yeh payload test ke liye bhej rahe hain
payload = {
    "email": "test@dxd.com",
    "task": "api-testing-task",
    "summary": {
        "programs": {
            "Chrome": "10.0 mins",
            "VSCode": "20.0 mins"
        },
        "categories": {
            "Browsers": "10.0 mins",
            "Development": "20.0 mins"
        }
    }
}

# ✅ CSRF ko avoid karne ke liye Referer zaroori hoti hai Django ke liye
headers = {
    "Content-Type": "application/json",
    "Referer": "https://dxdtime.ddsolutions.io"  # CSRF-safe check ke liye
}

try:
    print("📤 Sending request to:", url)
    response = requests.post(url, json=payload, headers=headers)
    print("✅ Status Code:", response.status_code)
    print("🧾 Response Body:\n", response.text)
    
    if response.status_code == 200:
        print("🎉 API accepted the data successfully!")
    elif response.status_code == 403:
        print("🚫 CSRF error: Please check if @csrf_exempt is applied on Django view.")
    else:
        print("⚠️ Unexpected response received.")

except Exception as e:
    print("❌ Error aya:", e)
