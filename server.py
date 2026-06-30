from __future__ import annotations
import sys
import os
import json
import importlib
import uuid
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# ==================== SFS2X DUMMY INJECTION ====================
def inject_sfs_dummies():
    class DummyRoom:
        def __init__(self, *args, **kwargs):
            self.id = 1
            self.name = "Plant Island"
        def getId(self): return self.id
        def getName(self): return self.name

    class DummyMessage:
        def __init__(self, *args, **kwargs): pass
        def getId(self): return 1

    for mod in ['sfs2x', 'sfs2x.core', 'sfs2x.protocol', 'sfs2x.transport']:
        if mod not in sys.modules:
            sys.modules[mod] = importlib.import_module('types').ModuleType(mod)

    sys.modules['sfs2x.protocol'].Room = DummyRoom
    sys.modules['sfs2x.protocol'].Message = DummyMessage

inject_sfs_dummies()

# ==================== DATABASE ====================
DB_FILE = "users_db.json"

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_db(db):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except:
        pass

def default_user(bbb_id):
    return {
        "user_id": str(uuid.uuid4()),
        "bbb_id": bbb_id,
        "session_token": str(uuid.uuid4()),
        "diamonds": 150,
        "coins": 20000,
        "relics": 40,
        "food": 5000,
        "level": 35,
        "prestige_level": 2,
        "islands": {
            "1": {
                "id": 1,
                "name": "Plant Island",
                "monsters": [
                    {"id": "MONSTER_A", "name": "Noggin", "level": 15, "happiness": 100, "x": 4, "y": 6}
                ]
            }
        },
        "monsters": ["MONSTER_A"]
    }

# ==================== HANDLER ====================
class MSMHandler(BaseHTTPRequestHandler):
    def log_message(self, *args): return

    def do_GET(self): self.process_request()
    def do_POST(self): self.process_request()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def process_request(self):
        parsed = urlparse(self.path)
        path = parsed.path.lower()
        # Leer body
        length = int(self.headers.get('Content-Length', 0))
        post_data = {}
        if length > 0:
            body = self.rfile.read(length).decode('utf-8', errors='ignore')
            try:
                post_data = json.loads(body) if 'json' in self.headers.get('Content-Type', '') else parse_qs(body)
                if isinstance(post_data, dict):
                    post_data = {k: v[0] if isinstance(v, list) else v for k, v in post_data.items()}
            except:
                pass

        params = {**dict(parse_qs(parsed.query)), **post_data}
        params = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}

        print(f"\n{'═'*75}")
        print(f"REQUEST → {self.command} {self.path}")
        print(f"PARAMS  → {params}")

        db = load_db()
        bbb_id = params.get("bbb_id") or params.get("id") or params.get("user_id") or "guest"
        user = db.setdefault(bbb_id, default_user(bbb_id))

        response = {"success": True, "server_time": int(time.time())}

        # 1. LOGIN / AUTENTICACIÓN
        if any(x in path for x in ["login", "auth", "connect", "session", "bigbluebubble"]):
            response = {
                "success": True,
                "session_token": user["session_token"],
                "user_id": user["user_id"],
                "player": user,
                "version": "5.4.2",
                "server_config": {"maintenance": False}
            }

        # 2. GET USER / CARGA DE DATOS
        elif any(x in path for x in ["get_user", "load", "profile", "user_data", "g_u_d"]):
            response = {
                "success": True,
                "player": user,
                "islands": user["islands"]
            }

        # 3. ACCIONES DEL JUEGO
        elif any(x in path for x in ["submit_action", "action", "cmd", "game", "breed", "collect"]):
            cmd = params.get("cmd") or params.get("action", "")
            
            if cmd in ["b_m", "start_breeding", "breed"]:
                is_rare = (time.time() % 9 < 2.5)
                monster = "MONSTERRARE_FLASQUE_v542" if is_rare else "MONSTER_NOGGIN"
                if is_rare and user["diamonds"] >= 15:
                    user["diamonds"] -= 15
                user.setdefault("monsters", []).append(monster)
                response.update({"monster_added": monster, "rare_trigger": is_rare})

            elif cmd in ["collect_currency", "collect"]:
                user["coins"] = user.get("coins", 0) + 3500
                response.update({"coins": user["coins"]})

            elif cmd in ["feed_monster", "feed"]:
                response.update({"happiness": 100})

            save_db(db)

        # 4. INFORMACIÓN DE ISLA
        elif any(x in path for x in ["island", "get_island"]):
            island_id = params.get("island_id", "1")
            response = {
                "success": True,
                "island": user["islands"].get(island_id, user["islands"].get("1"))
            }

        # Favicon y otras peticiones (como el servidor oficial)
        elif "favicon" in path:
            self.send_response(404)
            self.end_headers()
            return

        print(f"RESPONSE ← {response}")
        print(f"{'═'*75}\n")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

# ==================== INICIO DEL SERVIDOR ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9933))
    server = socketserver.ThreadingTCPServer(('0.0.0.0', port), MSMHandler)
    print(f"🚀 My Singing Monsters v5.4.2 - Servidor Emulado Activo")
    print(f"🌐 URL: http://0.0.0.0:{port}  (Railway la expone automáticamente)")
    print("✅ Listo para APK - Usa solo la URL base de Railway (sin puerto)")
    server.serve_forever()
