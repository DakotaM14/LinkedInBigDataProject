import requests

BASE_URL = "http://127.0.0.1:5000/"

# Make the request with the modified URL
result = requests.get(BASE_URL + "/city/San Diego, CA")

# Check if the request was successful (status code 200)
if result.status_code == 200:
    try:
        # Try to parse JSON data
        json_data = result.json()
        print(json_data)
    except requests.exceptions.JSONDecodeError:
        print("Response is not in JSON format.")
else:
    print(f"Request failed with status code: {result.status_code}")