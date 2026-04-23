import requests
import re
import time
import random
import os
import threading
import uuid
import SignerPy
from urllib.parse import urlencode
from pystyle import Colors, Colorate, Center
from colorama import Fore, init

init(autoreset=True)

stats = {"joined": 0, "likes": 0, "errors": 0, "gen": 0}
stats_lock = threading.Lock()
proxies_list = []
use_proxies = False

# =============================================================================
# GUEST SESSION GENERATOR (Aus tiktok_sessionid_gen.py)
# =============================================================================

def generate_guest_session():
    """Generiert eine anonyme Guest-Session ID."""
    url = "https://api.tiktokv.com/passport/guest/startup/?"
    params = urlencode({
        "scene": "normal",
        "device_type": "SM-N976N",
        "app_name": "musically_go",
        "version_name": "26.8.2",
        "device_id": str(random.randint(10**18, 10**19)),
        "aid": 1340,
        "device_platform": "android"
    })
    
    headers = {
        "user-agent": "com.zhiliaoapp.musically.go/260802 (Linux; U; Android 7.1.2; SM-N976N)",
        "host": "api.tiktokv.com"
    }

    try:
        response = requests.post(url + params, headers=headers, timeout=10)
        # Suche sessionid im Set-Cookie Header
        cookie = response.headers.get("Set-Cookie", "")
        sid = re.search(r"sessionid=([^;]+)", cookie)
        if sid:
            return sid.group(1)
    except:
        pass
    return None

def session_gen_launcher(amount):
    print(f"{Fore.YELLOW}[*] Generiere {amount} Guest-Sessions...")
    count = 0
    with open("ssid.txt", "a") as f:
        for _ in range(amount):
            sid = generate_guest_session()
            if sid:
                f.write(f"{sid}\n")
                count += 1
                print(f"{Fore.GREEN}[+] SID generiert: {sid[:15]}...")
            time.sleep(0.5)
    print(f"{Fore.CYAN}[!] Fertig! {count} IDs in ssid.txt gespeichert.")

# =============================================================================
# LIVE VIEW ENGINE (WEBCAST)
# =============================================================================

def live_worker(sid, room_id):
    global stats
    time.sleep(random.uniform(0.5, 10.0))
    proxy = None # Hier get_proxy() einbauen falls gewünscht
    
    params = {
        "room_id": room_id,
        "aid": "1988",
        "device_platform": "android",
        "version_code": "370805"
    }
    headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
    
    try:
        # 1. Room Enter
        requests.post("https://webcast16-normal-c-alisg.tiktokv.com/webcast/room/enter/", 
                      params=params, headers=headers, timeout=10)
        with stats_lock: stats["joined"] += 1
        
        # 2. Keep-Alive Loop
        while True:
            requests.get("https://webcast16-normal-c-alisg.tiktokv.com/webcast/room/ping/", 
                         params=params, headers=headers, timeout=7)
            time.sleep(20)
    except:
        with stats_lock: stats["errors"] += 1

# =============================================================================
# HAUPTMENÜ
# =============================================================================

def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(Colorate.Horizontal(Colors.red_to_purple, Center.XCenter("TIKTOK OVERLORD v17")))
    
    print(f"\n[1] Live Booster (Nutze session.txt - Echte Accs)")
    print(f"[2] Live Booster (Nutze ssid.txt - Guest-IDs)")
    print(f"[3] Video Viewbot / Sharebot")
    print(f"[4] Room-ID Finder")
    print(f"{Fore.GREEN}[5] Guest-Session Generator (IDs für Viewer-Boost erstellen)")
    
    choice = input("\nAuswahl > ")

    if choice == '5':
        anzahl = int(input("Wieviele Session-IDs sollen generiert werden? "))
        session_gen_launcher(anzahl)
        input("\nZurück zum Menü..."); main()

    elif choice == '2':
        room = input("Room-ID: ")
        if not os.path.exists("ssid.txt"): 
            print("ssid.txt nicht gefunden! Erst Punkt [5] nutzen."); return
            
        with open("ssid.txt", "r") as f:
            ids = [l.strip() for l in f if l.strip()]
        
        print(f"Starte Boost mit {len(ids)} Guest-IDs...")
        for sid in ids:
            threading.Thread(target=live_worker, args=(sid, room), daemon=True).start()
        
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            print(f"Boost läuft... Viewer: {stats['joined']} | Errors: {stats['errors']}")
            time.sleep(5)

if __name__ == "__main__":
    main()
