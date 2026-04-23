import requests
import re
import time
import random
import os
import threading
import uuid
import SignerPy
from pystyle import Colors, Colorate, Center
from colorama import Fore, init

init(autoreset=True)

# Globale Variablen
stats = {"joined": 0, "valid_sids": 0, "bad_sids": 0, "proxies": 0, "errors": 0}
proxies_list = []
valid_proxies = []

# =============================================================================
# PROXY SCRAPER & TESTER (NEU)
# =============================================================================

def scrape_proxies():
    """Zieht Proxys von öffentlichen Listen."""
    print(f"{Fore.YELLOW}[*] Scrape Proxys...")
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    ]
    scraped = []
    for s in sources:
        try:
            r = requests.get(s, timeout=10)
            if r.status_code == 200:
                scraped.extend(r.text.splitlines())
        except: pass
    return list(set(scraped))

def test_proxy(proxy_str):
    """Prüft, ob der Proxy die TikTok-API erreicht."""
    proxy = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
    try:
        # Test gegen den echten Endpoint
        r = requests.get("https://api-va.tiktokv.com/aweme/v1/feed/", proxies=proxy, timeout=3)
        if r.status_code == 200:
            valid_proxies.append(proxy_str)
            return True
    except: pass
    return False

def proxy_manager():
    global valid_proxies
    raw = scrape_proxies()
    print(f"{Fore.CYAN}[*] Teste {len(raw)} Proxys auf TikTok-Erreichbarkeit...")
    threads = []
    for p in raw[:500]: # Limit auf 500 für Speed
        t = threading.Thread(target=test_proxy, args=(p,))
        threads.append(t)
        t.start()
        if len(threads) > 50: # Semaphore-Ersatz
            for t in threads: t.join()
            threads = []
    print(f"{Fore.GREEN}[+] {len(valid_proxies)} valide Proxys bereit!")

# =============================================================================
# SESSION CHECKER (NEU)
# =============================================================================

def check_session(sid):
    """Prüft, ob eine Session ID noch gültig ist."""
    url = "https://api-va.tiktokv.com/passport/auth/status/"
    headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        # Wenn wir User-Daten zurückbekommen, ist die Session valide
        return data.get("data", {}).get("is_login", False) or "user_id" in str(data)
    except: return False

def validate_all_sessions(file_path):
    if not os.path.exists(file_path): return
    print(f"{Fore.YELLOW}[*] Checke Sessions in {file_path}...")
    valid = []
    with open(file_path, "r") as f:
        sids = [line.strip().split(":")[0] for line in f if line.strip()]
    
    for s in sids:
        if check_session(s):
            valid.append(s)
            print(f"{Fore.GREEN}[LIVE] {s[:10]}...")
        else:
            print(f"{Fore.RED}[DEAD] {s[:10]}...")
    
    with open(file_path, "w") as f:
        for v in valid: f.write(f"{v}\n")
    print(f"{Fore.CYAN}[!] {len(valid)} Sessions verbleibend.")

# =============================================================================
# MAIN UI
# =============================================================================

def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(Colorate.Horizontal(Colors.blue_to_white, Center.XCenter("TIKTOK OVERLORD v18\n[VALIDATOR & SCRAPER EDITION]")))
    
    print(f"\n[1] Live Booster (Guest/Acc)")
    print(f"[2] Room-ID Finder")
    print(f"[3] Session Generator (ssid.txt)")
    print(f"--- MANAGEMENT ---")
    print(f"{Fore.GREEN}[4] Checke sessions.txt (Echte Accs)")
    print(f"{Fore.GREEN}[5] Checke ssid.txt (Guest IDs)")
    print(f"{Fore.CYAN}[6] Scrape & Test Proxies")
    print(f"[E] Exit")
    
    choice = input("\nAuswahl > ")

    if choice == '4':
        validate_all_sessions("session.txt")
        input("Enter..."); main()
    elif choice == '5':
        validate_all_sessions("ssid.txt")
        input("Enter..."); main()
    elif choice == '6':
        proxy_manager()
        with open("proxies.txt", "w") as f:
            for p in valid_proxies: f.write(p + "\n")
        input("Enter..."); main()
    elif choice == '1':
        # Startet den Booster wie in v17, nutzt aber die valid_proxies falls vorhanden
        pass # Logik aus v17 hier einfügen...

if __name__ == "__main__":
    main()
