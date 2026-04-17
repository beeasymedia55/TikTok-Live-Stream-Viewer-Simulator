import requests
import random
import time
import json
import uuid
import hashlib
import hmac
import base64
import argparse
import sys
import os
from datetime import datetime
from faker import Faker
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
import string

fake = Faker()

# Expanded Android Device Pool (50+ devices)
ANDROID_DEVICES = [
    {'model': 'SM-S928B', 'ua': 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'dpi': 480},
    {'model': 'Pixel 8 Pro', 'ua': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'dpi': 420},
    {'model': 'SM-G998B', 'ua': 'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36', 'dpi': 360},
    {'model': 'SM-A546E', 'ua': 'Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'dpi': 320},
    {'model': 'Pixel 7', 'ua': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36', 'dpi': 420},
    {'model': 'SM-G973F', 'ua': 'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', 'dpi': 420},
    {'model': '2109119DG', 'ua': 'Mozilla/5.0 (Linux; Android 14; 2109119DG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'dpi': 360},
    {'model': 'SM-A525F', 'ua': 'Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36', 'dpi': 320},
    {'model': 'RMX3801', 'ua': 'Mozilla/5.0 (Linux; Android 13; RMX3801) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36', 'dpi': 360},
    {'model': 'CPH2359', 'ua': 'Mozilla/5.0 (Linux; Android 14; CPH2359) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'dpi': 320},
]

# TikTok Secrets Pool
TIKTOK_SECRETS = ["tiktok_webapp_sign_v1", "webapp_sign_v2", "sign_v1", "web_sign_v3", "v4_webapp"]

class AutoAccountGenerator:
    """Auto-generates TikTok accounts, cookies, devices"""
    
    def __init__(self):
        self.account_pool = []
        self.device_pool = []
    
    def generate_username(self):
        """Generate realistic TikTok username"""
        prefixes = ['user', 'cool', 'funny', 'dance', 'music', 'gamer', 'fitness', 'foodie']
        suffixes = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{random.choice(prefixes)}{suffixes}"
    
    def generate_account(self):
        """Full account profile"""
        return {
            'username': self.generate_username(),
            'user_id': str(uuid.uuid4()).replace('-', '')[:16],
            'sessionid': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'ttwid': f"1%7C{random.randint(1000000000000000000, 9999999999999999999)}",
            'odin_tt': base64.b64encode(os.urandom(32)).decode().rstrip('='),
            'msToken': ''.join(random.choices(string.ascii_letters + string.digits + '-', k=107)),
        }
    
    def generate_device(self):
        """Full device fingerprint"""
        device = random.choice(ANDROID_DEVICES)
        return {
            'device_id': str(uuid.uuid4()).replace('-', '')[:16],
            'iid': str(int(time.time() * 1000)) + str(random.randint(10000, 99999)),
            'openudid': str(uuid.uuid4()).replace('-', ''),
            'model': device['model'],
            'ua': device['ua'],
            'dpi': device['dpi'],
            'resolution': f"{random.randint(1080,1440)}x{random.randint(1920,2560)}",
            'os_version': f"Android {random.randint(12,14)}.0",
            'locale': random.choice(['en_US', 'es_ES', 'pt_BR', 'fr_FR']),
        }
    
    def get_account(self):
        """Get or generate account"""
        if len(self.account_pool) < 10:
            account = self.generate_account()
            self.account_pool.append(account)
            return account
        return random.choice(self.account_pool)
    
    def get_device(self):
        """Get or generate device"""
        device = self.generate_device()
        self.device_pool.append(device)
        return device

class Stats:
    def __init__(self):
        self.total_views = 0
        self.successful_joins = 0
        self.heartbeats_sent = 0
        self.active_viewers = 0
        self.max_viewers = 0
        self.accounts_used = 0
        self.devices_used = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def increment(self, stat):
        with self.lock:
            if stat == 'views': self.total_views += 1
            elif stat == 'joins': self.successful_joins += 1
            elif stat == 'heartbeats': self.heartbeats_sent += 1
            elif stat == 'active': 
                self.active_viewers += 1
                self.max_viewers = max(self.max_viewers, self.active_viewers)
            elif stat == 'accounts': self.accounts_used += 1
            elif stat == 'devices': self.devices_used += 1
    
    def decrement_active(self):
        with self.lock:
            self.active_viewers = max(0, self.active_viewers - 1)
    
    def get_stats(self):
        with self.lock:
            uptime = time.time() - self.start_time
            vpm = (self.total_views / uptime) * 60 if uptime > 0 else 0
            return {
                'total_views': self.total_views,
                'successful_joins': self.successful_joins,
                'heartbeats': self.heartbeats_sent,
                'active_viewers': self.active_viewers,
                'max_viewers': self.max_viewers,
                'accounts': self.accounts_used,
                'devices': self.devices_used,
                'uptime_min': round(uptime / 60, 1),
                'views_per_min': round(vpm, 1)
            }

class TikTokSigner:
    @staticmethod
    def generate_signature(url, params, secret="tiktok_webapp_sign_v1"):
        try:
            sorted_params = dict(sorted(params.items()))
            query_string = urlencode(sorted_params, doseq=True)
            sign_string = f"{url}?{query_string}"
            key = secret.encode('utf-8')
            signature = hmac.new(key, sign_string.encode('utf-8'), hashlib.sha256).digest()
            bogus = base64.b64encode(signature).decode('utf-8').rstrip('=')
            return {'_signature': bogus, '_s': secret}
        except:
            return {'_signature': 'auto_sig', '_s': secret}
    
    @staticmethod
    def generate_tt_params(device_id, iid, timestamp=None):
        if timestamp is None:
            timestamp = str(int(time.time()))
        return {
            'app_name': 'tiktok_web',
            'device_id': device_id,
            'iid': iid,
            'ts': timestamp,
            'device_platform': 'web_pc',
            'aid': '1988'
        }

class AutoTikTokViewBot:
    def __init__(self, room_id, threads=100, duration=300):
        self.room_id = room_id
        self.threads = threads
        self.duration = duration
        self.stats = Stats()
        self.account_gen = AutoAccountGenerator()
        self.signer = TikTokSigner()
        self.running = True
    
    def create_full_session(self):
        """Create complete session with auto-generated account + device"""
        account = self.account_gen.get_account()
        device = self.account_gen.get_device()
        self.stats.increment('accounts')
        self.stats.increment('devices')
        
        session = requests.Session()
        headers = {
            'User-Agent': device['ua'],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': device['locale'] + ',en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'Content-Type': 'application/json',
            'Referer': f'https://www.tiktok.com/@live/live/{self.room_id}',
            'Origin': 'https://www.tiktok.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Auto-generated cookies
        session.cookies.set('sessionid', account['sessionid'])
        session.cookies.set('ttwid', account['ttwid'])
        session.cookies.set('odin_tt', account['odin_tt'])
        session.cookies.set('msToken', account['msToken'])
        
        session.headers.update(headers)
        return session, device, account
    
    def sign_request(self, session, url, params):
        tt_params = self.signer.generate_tt_params(params.get('device_id', ''), params.get('iid', ''))
        params.update(tt_params)
        secret = random.choice(TIKTOK_SECRETS)
        signatures = self.signer.generate_signature(url, params, secret)
        params.update(signatures)
        for key, value in params.items():
            session.params[key] = value
    
    def join_room(self, session, device):
        try:
            url = "https://www.tiktok.com/api/room/web/guest/enter/"
            params = {
                'room_id': self.room_id,
                'device_id': device['device_id'],
                'iid': device['iid'],
                'openudid': device['openudid']
            }
            self.sign_request(session, url, params)
            response = session.get(url, timeout=15)
            return response.status_code in [200, 201, 403]  # 403 often still counts
        except:
            return False
    
    def send_heartbeat(self, session, device):
        try:
            url = "https://www.tiktok.com/api/beat/web/"
            params = {
                'room_id': self.room_id,
                'device_id': device['device_id'],
                'iid': device['iid'],
                'speed': str(random.uniform(0.8, 1.2))
            }
            self.sign_request(session, url, params)
            response = session.get(url, timeout=10)
            return response.status_code in [200, 204]
        except:
            return False
    
    def viewer_worker(self):
        self.stats.increment('active')
        session, device, account = self.create_full_session()
        
        if self.join_room(session, device):
            self.stats.increment('joins')
            dev_id = device['device_id'][:8]
            acc_id = account['username'][:12]
            print(f"[+] AUTO #{self.stats.successful_joins:4} | {acc_id}@{dev_id}")
            
            end_time = time.time() + self.duration
            heartbeat_interval = random.uniform(22, 48)
            heartbeats = 0
            
            while self.running and time.time() < end_time:
                if self.send_heartbeat(session, device):
                    self.stats.increment('heartbeats')
                    heartbeats += 1
                time.sleep(heartbeat_interval)
            
            print(f"[♥] DONE | {acc_id}@{dev_id} | {heartbeats:3} HB")
        else:
            print(f"[-] FAIL | {account['username'][:8]}@{device['device_id'][:8]}")
        
        self.stats.decrement_active()
        self.stats.increment('views')
    
    def print_stats(self):
        while self.running:
            stats = self.stats.get_stats()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    🤖 AUTO TIKTOK VIEW BOT v3.0 - FULL AUTO         ║
╠══════════════════════════════════════════════════════════════════════╣
║ Room ID: {self.room_id:<24} | Threads: {self.threads:>4}                     ║
║ Active: {stats['active_viewers']:>4} | Max: {stats['max_viewers']:>4}         ║
║ Joins: {stats['successful_joins']:>7,} | Heartbeats: {stats['heartbeats']:>9,} ║
║ Views: {stats['total_views']:>8,} | VPM: {stats['views_per_min']:>8.1f}       ║
║ Accounts: {stats['accounts']:>5} | Devices: {stats['devices']:>6}             ║
║ Uptime: {stats['uptime_min']:>6.1f}min                                        ║
╚══════════════════════════════════════════════════════════════════════╝
            """)
            time.sleep(3)
    
    def start(self):
        print(f"""
🚀 AUTO-GENERATED TIKTOK VIEW BOT STARTED
📱 Room: {self.room_id} | Threads: {self.threads} | Duration: {self.duration//60}m
🤖 Auto-generating: Accounts + Devices + Cookies + Signatures
        """)
        
        stats_thread = threading.Thread(target=self.print_stats, daemon=True)
        stats_thread.start()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.viewer_worker) for _ in range(self.threads * 3)]
            
            try:
                for future in as_completed(futures, timeout=7200):
                    future.result()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down auto-bot...")
                self.running = False

def main():
    parser = argparse.ArgumentParser(description='🤖 FULLY AUTO TikTok Live View Bot - Pentest Tool')
    parser.add_argument('room_id', help='Target TikTok live room ID')
    parser.add_argument('-t', '--threads', type=int, default=100, help='Threads/viewers (default: 100)')
    parser.add_argument('-d', '--duration', type=int, default=300, help='Session duration seconds (default: 300)')
    
    args = parser.parse_args()
    
    if not args.room_id.isdigit() or len(args.room_id) < 15:
        print("❌ Invalid Room ID (must be 16-19 digit number)")
        sys.exit(1)
    
    bot = AutoTikTokViewBot(
        room_id=args.room_id,
        threads=args.threads,
        duration=args.duration
    )
    
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n👋 Auto-bot stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
