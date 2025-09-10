from flask import Flask, request, Response, jsonify
import requests
import logging
import re

app = Flask(__name__)

# Logging (dosyaya yaz)
logging.basicConfig(
    filename='vesika_proxy.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

TARGET_BASE = "https://quantrexsystems.alwaysdata.net/diger/ozel/vesika/jessyvesika.php"

# Basit TC doğrulama: sadece rakamlar, uzunluk 5-20 arası (gerektiğinde değiştir)
TC_RE = re.compile(r'^\d{5,20}$')

@app.route('/vesika', methods=['GET'])
def vesika_proxy():
    tc = request.args.get('tc', '').strip()
    if not tc:
        return jsonify({"error": "Eksik parametre: tc"}), 400

    if not TC_RE.match(tc):
        return jsonify({"error": "Geçersiz tc formatı (sadece rakam, 5-20 hane)"}), 400

    # Hedef URL'ye parametre ile istek at
    try:
        # Eğer özel bir header/timeout istersen burayı değiştir
        resp = requests.get(TARGET_BASE, params={'tc': tc}, timeout=10)
    except requests.exceptions.RequestException as e:
        logging.error("Request failed for tc=%s: %s", tc, str(e))
        return jsonify({"error": "Hedef siteye istek atılamadı", "details": str(e)}), 502

    # Log
    logging.info("tc=%s -> %s (status=%s)", tc, resp.url, resp.status_code)

    # Hedef cevabını olduğu gibi döndür (content-type'ı koru)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
    return Response(resp.content, status=resp.status_code, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
