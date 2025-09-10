import os
import requests
from redis import Redis

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
TARGET = "https://quantrexsystems.alwaysdata.net/diger/ozel/vesika/jessyvesika.php"

def do_request(tc):
    try:
        s = requests.Session()
        r = s.get(TARGET, params={"tc": tc}, timeout=60)
        # cache sonucu 10 dakika sakla (uydur: ihtiyaca göre değiştir)
        redis_conn.setex(f"vesika:result:{tc}", 600, r.content)
        return {"status": "ok", "code": r.status_code}
    except Exception as e:
        redis_conn.setex(f"vesika:result:{tc}", 120, f"ERROR: {e}")
        return {"status":"error", "error": str(e)}
