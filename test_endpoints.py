"""
Videoflix API Endpoint Test Script
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api"
TEST_EMAIL = "testuser@videoflix.com"
TEST_PASSWORD = "TestPass123!"

session = requests.Session()


def test(name, method, url, expected, json_data=None, use_session=True):
    client = session if use_session else requests
    if method == "GET":
        r = client.get(url)
    else:
        r = client.post(url, json=json_data)

    status = (
        "PASS"
        if r.status_code == expected
        or (isinstance(expected, list) and r.status_code in expected)
        else "FAIL"
    )
    print(f"[{status}] {method} {url} -> {r.status_code} (expected {expected})")
    return r


print("\n=== VIDEOFLIX API TESTS ===\n")

# 1. Register
print("\n--- REGISTRIERUNG ---")
test(
    "Register",
    "POST",
    f"{BASE_URL}/register/",
    201,
    {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirmed_password": TEST_PASSWORD,
    },
)

# 2. Register Duplicate
test(
    "Register Duplicate",
    "POST",
    f"{BASE_URL}/register/",
    400,
    {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirmed_password": TEST_PASSWORD,
    },
)

# 3. Login (inactive)
print("\n--- LOGIN (INAKTIV) ---")
test(
    "Login Inactive",
    "POST",
    f"{BASE_URL}/login/",
    400,
    {"email": TEST_EMAIL, "password": TEST_PASSWORD},
)

print("\n>>> JETZT: User in Mailhog (http://localhost:8025) aktivieren! <<<")
input(">>> Druecke ENTER wenn aktiviert...")

# 4. Login (active)
print("\n--- LOGIN (AKTIV) ---")
test(
    "Login",
    "POST",
    f"{BASE_URL}/login/",
    200,
    {"email": TEST_EMAIL, "password": TEST_PASSWORD},
)

# 5. Login wrong password
test(
    "Login Wrong PW",
    "POST",
    f"{BASE_URL}/login/",
    400,
    {"email": TEST_EMAIL, "password": "WrongPass!"},
    use_session=False,
)

# 6. Video List
print("\n--- VIDEO ENDPOINTS ---")
test("Video List", "GET", f"{BASE_URL}/video/", 200)
test("Video No Auth", "GET", f"{BASE_URL}/video/", [401, 403], use_session=False)
test("Video 404", "GET", f"{BASE_URL}/video/9999/480p/index.m3u8", 404)

# 7. Token Refresh
print("\n--- TOKEN REFRESH ---")
test("Token Refresh", "POST", f"{BASE_URL}/token/refresh/", 200)
test(
    "Token Refresh No Token",
    "POST",
    f"{BASE_URL}/token/refresh/",
    400,
    use_session=False,
)

# 8. Password Reset
print("\n--- PASSWORD RESET ---")
test(
    "Password Reset", "POST", f"{BASE_URL}/password_reset/", 200, {"email": TEST_EMAIL}
)
test(
    "Password Reset Unknown",
    "POST",
    f"{BASE_URL}/password_reset/",
    200,
    {"email": "unknown@test.com"},
)

# 9. Static Content
print("\n--- STATIC CONTENT ---")
test("Privacy", "GET", f"{BASE_URL}/privacy/", 200, use_session=False)
test("Imprint", "GET", f"{BASE_URL}/imprint/", 200, use_session=False)

# 10. Logout
print("\n--- LOGOUT ---")
test("Logout", "POST", f"{BASE_URL}/logout/", 200)
test("Video After Logout", "GET", f"{BASE_URL}/video/", [401, 403])

print("\n=== TESTS ABGESCHLOSSEN ===\n")
