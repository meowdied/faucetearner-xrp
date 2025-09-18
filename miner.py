import requests
import time
import getpass
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# init colorama for Windows
init(autoreset=True)

LOGIN_URL = "https://faucetearner.org/api.php?act=login"
FAUCET_API_URL = "https://faucetearner.org/api.php?act=faucet"
DASHBOARD_URL = "https://faucetearner.org/dashboard.php"

# ---------------- ASK FOR CREDS ----------------
print(Fore.WHITE + "Enter your account credentials")
USERNAME = input(Fore.WHITE + "Username or email: ")
PASSWORD = getpass.getpass(Fore.WHITE + "Password: ")
# -----------------------------------------------

session = requests.Session()

# Send login as JSON to the right endpoint
login_data = {
    "email": USERNAME,
    "password": PASSWORD
}
login_resp = session.post(LOGIN_URL, json=login_data)

try:
    login_json = login_resp.json()
except Exception:
    print(Fore.RED + "[-] Login response not JSON:", login_resp.text[:200])
    input("Press Enter to exit...")
    exit(1)

if login_json.get("code") != 0:
    print(Fore.RED + f"[-] Login failed: {login_json.get('message', 'Unknown error')}")
    input("Press Enter to exit...")
    exit(1)

print(Fore.GREEN + "[+] Logged in successfully!")


def get_balance():
    """Fetch XRP balance from dashboard page."""
    r = session.get(DASHBOARD_URL)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    stat_div = soup.find("div", class_="stat-number")
    if stat_div:
        balance = stat_div.get_text(strip=True).replace("XRP", "").strip()
        return balance
    return None


def claim_faucet():
    """Call faucet API and print result + balance."""
    resp = session.post(FAUCET_API_URL)
    if resp.status_code != 200:
        print(Fore.RED + f"[-] Claim request failed, status: {resp.status_code}")
        return False

    try:
        j = resp.json()
    except Exception:
        print(Fore.RED + f"[-] Claim response not JSON, raw: {resp.text[:200]}")
        return False

    code = j.get("code")
    msg = j.get("message", "")

    if code == 0:
        # Extract reward from message HTML
        reward_match = re.search(r'>([\d.]+ XRP)<', msg)
        reward = reward_match.group(1) if reward_match else "?"
        balance = get_balance()
        print(Fore.GREEN + f"[+] Claimed {reward} | Balance: {balance if balance else '?'} XRP")
        return True

    elif code == 2:
        # Cooldown
        print(Fore.YELLOW + f"[!] Cooldown: {msg}")
        return "cooldown"

    else:
        print(Fore.RED + f"[-] Claim failed: {msg}")
        return False


# Main loop
while True:
    result = claim_faucet()
    if result is True or result == "cooldown":
        time.sleep(60)  # always wait 1 minute
    else:
        time.sleep(10)  # retry after 10s if unknown error
