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

# Globale Variablen
stats = {"joined": 0, "likes": 0, "views": 0, "shares": 0, "errors": 0}
stats_lock = threading.Lock()
valid_proxies = []
use_proxies = False

SAMSUNG_DEVICES = ["SM-G9900", "SM-A528B", "SM-F711B", "SM-F926B", "SM-N976N", "SM-A525F", "SM-M526BR"]

# =============================================================================
# PROXY SCRAPER & TESTER
# =============================================================================

def scrape_proxies():
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    ]
    scraped = []
    for s in sources:
        try:
            r = requests.get(s, timeout=7)
            if r.status_code == 200: scraped.extend(r.text.splitlines())
        except: pass
    return list(set(scraped))

def test_proxy(proxy_str):
    proxy = {"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}
    try:
        r = requests.get("https://api-va.tiktokv.com/aweme/v1/feed/", proxies=proxy, timeout=4)
        if r.status_code == 200:
            valid_proxies.append(proxy_str)
            return True
    except: pass
    return False

def proxy_manager():
    global valid_proxies
    valid_proxies = []
    raw = scrape_proxies()
    print(f"{Fore.CYAN}[*] Teste {len(raw)} Proxys auf TikTok-Erreichbarkeit (3-5 Min)...")
    threads = []
    for p in raw[:800]: # Checke max 800 für Speed
        t = threading.Thread(target=test_proxy, args=(p,))
        threads.append(t)
        t.start()
        if len(threads) > 80:
            for t in threads: t.join()
            threads = []
    for t in threads: t.join()
    
    with open("proxies.txt", "w") as f:
        for p in valid_proxies: f.write(p + "\n")
    print(f"{Fore.GREEN}[+] {len(valid_proxies)} schnelle Proxys bereit!")

def auto_proxy_updater():
    """Lädt alle 10 Minuten im Hintergrund neue Proxys."""
    while True:
        time.sleep(600)
        raw = scrape_proxies()
        for p in raw[:300]: threading.Thread(target=test_proxy, args=(p,)).start()

# =============================================================================
# SESSION GENERATOR & CHECKER
# =============================================================================

def check_session(sid):
    url = "https://api-va.tiktokv.com/passport/auth/status/"
    headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
    try:
        r = requests.get(url, headers=headers, timeout=5).json()
        return r.get("data", {}).get("is_login", False) or "user_id" in str(r)
    except: return False

def validate_all_sessions(file_path):
    if not os.path.exists(file_path): 
        print(f"{Fore.RED}[!] {file_path} nicht gefunden."); return
    print(f"{Fore.YELLOW}[*] Checke Sessions in {file_path}...")
    
    with open(file_path, "r") as f: sids = [l.strip().split(":")[0] for l in f if l.strip()]
    valid = []
    for s in sids:
        if check_session(s):
            valid.append(s); print(f"{Fore.GREEN}[LIVE] {s[:15]}...")
        else: print(f"{Fore.RED}[DEAD] {s[:15]}...")
    
    with open(file_path, "w") as f:
        for v in valid: f.write(f"{v}\n")
    print(f"{Fore.CYAN}[!] {len(valid)} valide Sessions verbleibend.")

def generate_guest_session():
    url = "https://api.tiktokv.com/passport/guest/startup/?"
    params = urlencode({"scene": "normal", "device_type": "SM-N976N", "app_name": "musically_go", "version_name": "26.8.2", "device_id": str(random.randint(10**18, 10**19)), "aid": 1340, "device_platform": "android"})
    headers = {"user-agent": "com.zhiliaoapp.musically.go/260802 (Linux; U; Android 7.1.2; SM-N976N)", "host": "api.tiktokv.com"}
    try:
        r = requests.post(url + params, headers=headers, timeout=10)
        sid = re.search(r"sessionid=([^;]+)", r.headers.get("Set-Cookie", ""))
        if sid: return sid.group(1)
    except: pass
    return None

def session_gen_launcher(amount):
    print(f"{Fore.YELLOW}[*] Generiere {amount} Guest-Sessions (ssid.txt)...")
    count = 0
    with open("ssid.txt", "a") as f:
        for _ in range(amount):
            sid = generate_guest_session()
            if sid:
                f.write(f"{sid}\n"); count += 1
                print(f"{Fore.GREEN}[+] SID: {sid[:15]}...")
    print(f"{Fore.CYAN}[!] {count} IDs generiert.")

def make_tiktok_params(aid="1233"):
    return {
        "passport-sdk-version": "6031990", "device_platform": "android", "os": "android", "ssmix": "a",
        "_rticket": str(int(time.time() * 1000)), "cdid": str(uuid.uuid4()), "aid": aid,
        "app_name": "musical_ly", "version_code": "370805", "version_name": "37.8.5",
        "manifest_version_code": "370805", "update_version_code": "370805",
        "device_brand": "samsung", "device_type": random.choice(SAMSUNG_DEVICES),
        "os_version": "12", "device_id": str(random.randint(10**18, 10**19-1)),
        "iid": str(random.randint(10**18, 10**19-1)), "resolution": "1080*1920", "dpi": "480"
    }# =============================================================================
# BOOSTER ENGINES (VIEWS, SHARES, LIVE)
# =============================================================================

def get_proxy():
    if not use_proxies or not valid_proxies: return None
    p = random.choice(valid_proxies)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def grab_room_id(username):
    username = username.replace("@", "").strip()
    try:
        r = requests.get(f"https://www.tiktok.com/@{username}/live", headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
        match = re.search(r'\"roomId\":\"(\d+)\"', r)
        return match.group(1) if match else None
    except: return None

def video_booster_worker(video_id, mode):
    global stats
    while True:
        try:
            proxy = get_proxy()
            params = make_tiktok_params()
            url = f"https://api-va.tiktokv.com/aweme/v1/aweme/stats/"
            payload = f"item_id={video_id}&share_delta=1" if mode == "shares" else f"aweme_id={video_id}&play_delta=1"
            
            sig = SignerPy.sign(params=params, payload=payload)
            headers = {
                "User-Agent": "com.zhiliaoapp.musically/2023708050",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Gorgon": sig.get("x-gorgon"), "X-Khronos": sig.get("x-khronos")
            }

            r = requests.post(url, params=params, data=payload, headers=headers, proxies=proxy, timeout=7)
            if r.status_code == 200:
                with stats_lock:
                    if mode == "shares": stats["shares"] += 1
                    else: stats["views"] += 1
            else:
                with stats_lock: stats["errors"] += 1
            time.sleep(random.uniform(0.1, 0.5))
        except:
            with stats_lock: stats["errors"] += 1

def live_worker(sid, room_id):
    global stats
    time.sleep(random.uniform(0.5, 12.0))
    proxy = get_proxy()
    domain = random.choice(["https://webcast16-normal-c-alisg.tiktokv.com", "https://webcast16-normal-useast2a.tiktokv.com"])
    
    params = make_tiktok_params(aid="1988")
    params.update({"room_id": room_id, "scene": "live_room"})
    headers = {"Cookie": f"sessionid={sid}", "User-Agent": "com.zhiliaoapp.musically/2023708050"}
    payload = {"room_id": str(room_id)}
    
    try:
        sig = SignerPy.sign(params=params, payload=payload)
        headers.update({"X-Gorgon": sig.get("x-gorgon"), "X-Khronos": sig.get("x-khronos")})
        requests.post(f"{domain}/webcast/room/enter/", params=params, data=payload, headers=headers, proxies=proxy, timeout=10)
        with stats_lock: stats["joined"] += 1
        
        while True:
            requests.get(f"{domain}/webcast/room/ping/", params=params, headers=headers, proxies=proxy, timeout=5)
            if random.random() > 0.8:
                requests.post(f"{domain}/webcast/stats/heart/", params=params, headers=headers, proxies=proxy)
                with stats_lock: stats["likes"] += 1
            time.sleep(random.randint(15, 25))
    except:
        with stats_lock: stats["errors"] += 1

# =============================================================================
# UI & MAIN LOOP
# =============================================================================

def dashboard_thread():
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        print(Colorate.Horizontal(Colors.blue_to_white, Center.XCenter("TIKTOK OVERLORD v18 | DASHBOARD")))
        print(f"\n {Fore.GREEN}Live Viewer : {stats['joined']}    {Fore.CYAN}Views  : {stats['views']}")
        print(f" {Fore.MAGENTA}Live Likes  : {stats['likes']}    {Fore.YELLOW}Shares : {stats['shares']}")
        print(f" {Fore.RED}Errors      : {stats['errors']}")
        print(f"\n {Fore.WHITE}Aktive Proxys: {len(valid_proxies)} (Auto-Update läuft) | Threads: {threading.active_count()-3}")
        time.sleep(2)

def main():
    global use_proxies, valid_proxies
    os.system('clear' if os.name != 'nt' else 'cls')
    
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f: valid_proxies = [l.strip() for l in f if l.strip()]

    print(Colorate.Horizontal(Colors.red_to_blue, Center.XCenter("TIKTOK OVERLORD v18\n[VALIDATOR & AUTO-PROXY EDITION]")))
    print(f"\n[1] Live Booster (Nutze session.txt - Echte Accs)")
    print(f"[2] Live Booster (Nutze ssid.txt - Guest IDs)")
    print(f"[3] Video Viewbot (Fast)")
    print(f"[4] Video Sharebot (Ranking)")
    print(f"--- MANAGEMENT ---")
    print(f"{Fore.GREEN}[5] Checke session.txt")
    print(f"{Fore.GREEN}[6] Checke ssid.txt")
    print(f"{Fore.YELLOW}[7] Generiere Guest-IDs (ssid.txt)")
    print(f"{Fore.CYAN}[8] Scrape & Test Proxys (Neu laden)")
    
    choice = input("\nAuswahl > ")

    if choice in ['5', '6']:
        validate_all_sessions("session.txt" if choice == '5' else "ssid.txt")
        input("\nEnter..."); main()
    elif choice == '7':
        amt = int(input("Wieviele IDs? "))
        session_gen_launcher(amt); input("\nEnter..."); main()
    elif choice == '8':
        proxy_manager(); input("\nEnter..."); main()
    elif choice in ['1', '2', '3', '4']:
        target = input("ID oder Username (@): ")
        if choice in ['1', '2'] and not target.isdigit(): target = grab_room_id(target)
        if not target: print("ID nicht gefunden!"); time.sleep(2); main()
        
        use_proxies = input("Proxys nutzen? (y/n): ").lower() == 'y'
        
        if use_proxies:
            threading.Thread(target=auto_proxy_updater, daemon=True).start()
        
        threading.Thread(target=dashboard_thread, daemon=True).start()

        if choice in ['1', '2']:
            file_name = "session.txt" if choice == '1' else "ssid.txt"
            if not os.path.exists(file_name): print(f"{file_name} fehlt!"); exit()
            with open(file_name, "r") as f: sids = [l.strip().split(":")[0] for l in f]
            for sid in sids: threading.Thread(target=live_worker, args=(sid, target), daemon=True).start()
        else:
            threads = int(input("Threads: "))
            mode = "views" if choice == '3' else "shares"
            for _ in range(threads): threading.Thread(target=video_booster_worker, args=(target, mode), daemon=True).start()
        
        while True: time.sleep(1)

if __name__ == "__main__":
    main()


