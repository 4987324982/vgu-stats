# ВГУstats — локальный бэкенд (только стандартная библиотека Python, установок не нужно)
# Запуск:  python server.py   (или  py server.py)
# Сайт:    http://localhost:8555/
# С телефона: http://<IP-компьютера>:8555/

import json
import os
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data.json")
PORT = int(os.environ.get("VGUSTATS_PORT", "8555"))
HOST = "0.0.0.0"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (ValueError, OSError):
            pass
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/data":
            self._json(200, load_data())
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/data":
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                self._json(400, {"error": "bad json"})
                return
            save_data(data)
            self._json(200, {"ok": True})
            return
        self._json(404, {"error": "not found"})

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    ip = local_ip()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("=" * 52)
    print(" ВГУstats бэкенд запущен")
    print(f"  На этом компьютере:  http://localhost:{PORT}/")
    print(f"  С телефона (Wi-Fi):   http://{ip}:{PORT}/")
    print("  Остановить:  Ctrl + C")
    print("=" * 52)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n Остановлен.")