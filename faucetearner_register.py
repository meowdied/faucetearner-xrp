import requests
import csv
import getpass
import time
import os
import json

# Registration API
REGISTER_URL = "https://faucetearner.org/api.php?act=register"

# Headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_CSV = "successful_accounts.csv"
OUTPUT_JSON = "successful_accounts.json"

# ---------- Save Functions ----------
def save_account_csv(username, email, password):
    file_exists = os.path.isfile(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline='', encoding='utf-8') as csvfile:
        fieldnames = ["username", "email", "password"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"username": username, "email": email, "password": password})

def save_account_json(username, email, password):
    account = {"username": username, "email": email, "password": password}
    data = []

    # Load existing JSON if present
    if os.path.isfile(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []

    # Append new account
    data.append(account)

    # Save back to file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_account(username, email, password):
    save_account_csv(username, email, password)
    save_account_json(username, email, password)

# ---------- Registration ----------
def register_account(session, username, email, password):
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password,
        "agree": 1
    }
    try:
        resp = session.post(REGISTER_URL, data=payload, headers=HEADERS)
        j = resp.json()
    except Exception as e:
        print(f"[-] Error for {username}: {e}")
        return False

    if j.get("code") == 0:
        print(f"[+] Account created: {username} | {email}")
        save_account(username, email, password)
        return True
    else:
        print(f"[-] Failed to create {username} | {email}: {j.get('message')}")
        return False

# ---------- Modes ----------
def manual_registration(session):
    print("=== Manual Registration ===")
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")
    register_account(session, username, email, password)

def csv_registration(session, path):
    print(f"=== CSV Registration: {path} ===")
    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row.get("username")
                email = row.get("email")
                password = row.get("password")
                if all([username, email, password]):
                    if register_account(session, username, email, password):
                        time.sleep(1)  # Small delay
    except Exception as e:
        print(f"[-] Error reading CSV: {e}")

# ---------- MAIN ----------
if __name__ == "__main__":
    session = requests.Session()

    print("Choose registration mode:")
    print("1. Manual registration")
    print("2. CSV registration")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        manual_registration(session)
    elif choice == "2":
        path = input("Enter path to CSV file: ").strip()
        csv_registration(session, path)
    else:
        print("Invalid choice. Exiting.")
