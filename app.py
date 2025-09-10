import os
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
import time

app = Flask(__name__)
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(redis_url)
q = Queue(connection=redis_conn)

# Basit health
@app.route("/health")
def health():
    return "ok", 200

# enqueue endpoint
@app.route("/vesika", methods=["GET"])
def vesika_enqueue():
    tc = request.args.get("tc", "").strip()
    if not tc:
        return jsonify({"error": "tc gerekli"}), 400

    # Eğer cache varsa hızlı geri dön
    cache_key = f"vesika:result:{tc}"
    cached = redis_conn.get(cache_key)
    if cached:
        return cached, 200, {"Content-Type": "text/html"}

    # enqueue job
    job = q.enqueue("worker.do_request", tc, job_timeout=600)
    return jsonify({"status": "queued", "job_id": job.id}), 202

# polling result
@app.route("/vesika/result", methods=["GET"])
def vesika_result():
    tc = request.args.get("tc", "").strip()
    cache_key = f"vesika:result:{tc}"
    cached = redis_conn.get(cache_key)
    if cached:
        return cached, 200, {"Content-Type": "text/html"}
    return jsonify({"status":"processing"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
