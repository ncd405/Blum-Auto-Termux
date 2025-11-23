import asyncio
import requests
import random
import time
import threading
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.functions.messages import RequestWebView
from urllib.parse import unquote
from flask import Flask

# CONFIG
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STR = os.getenv("SESSION_STRING", "")
BLUM_BOT = "BlumCryptoBot"
BLUM_URL = "https://telegram.blum.codes/"
BASE_API = "https://game-domain.blum.codes/api/v1" 

# FAKE SERVER
app = Flask(__name__)
@app.route('/')
def home(): return "Blum Hunter is Running!"
def run_web(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# CORE
class BlumSniper:
    def __init__(self):
        try:
            self.client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
            self.headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)", "Origin": "https://telegram.blum.codes", "Accept": "application/json"}
            self.token = None
        except Exception as e:
            print(f"Init Error: {e}")

    async def login(self):
        if not SESSION_STR:
            print("MISSING SESSION_STRING")
            return False
        await self.client.connect()
        try:
            web = await self.client(RequestWebView(peer=BLUM_BOT, bot=BLUM_BOT, platform='ios', from_bot_menu=False, url=BLUM_URL))
            query = unquote(web.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            res = requests.post("https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", json={"query": query}, headers=self.headers)
            if res.status_code == 200:
                self.token = res.json().get("token").get("access")
                self.headers["Authorization"] = f"Bearer {self.token}"
                print("✅ Login Blum OK")
                return True
        except Exception as e: print(f"❌ Login Fail: {e}")
        finally: await self.client.disconnect()
        return False

    def run(self):
        if not self.token: return
        # Farm
        try:
            bal = requests.get(f"{BASE_API}/user/balance", headers=self.headers).json()
            farm = bal.get("farming")
            if farm:
                if int(time.time()*1000) > farm.get("endTime"):
                    requests.post(f"{BASE_API}/farming/claim", headers=self.headers); print("🌾 Claimed Farm")
                    requests.post(f"{BASE_API}/farming/start", headers=self.headers); print("🚜 Started Farm")
            else: requests.post(f"{BASE_API}/farming/start", headers=self.headers); print("🚜 Started Farm")
        except: pass
        
        # Game
        try:
            bal = requests.get(f"{BASE_API}/user/balance", headers=self.headers).json()
            tickets = bal.get("playPasses", 0)
            while tickets > 0:
                res = requests.post(f"{BASE_API}/game/play", headers=self.headers)
                if res.status_code == 200:
                    gid = res.json().get("gameId")
                    wait = random.randint(32, 38)
                    print(f"🎮 Playing... wait {wait}s")
                    time.sleep(wait)
                    pts = random.randint(190, 220)
                    requests.post(f"{BASE_API}/game/claim", json={"gameId": gid, "points": pts}, headers=self.headers)
                    print(f"🏆 Won {pts} pts")
                    tickets -= 1
                    time.sleep(5)
                else: break
        except: pass

async def loop():
    bot = BlumSniper()
    while True:
        if await bot.login(): bot.run()
        s = 3600 + random.randint(100, 500)
        print(f"💤 Sleep {s}s...")
        await asyncio.sleep(s)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(loop())
