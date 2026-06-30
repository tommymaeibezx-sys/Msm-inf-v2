from __future__ import annotations
import sys
import os
import json
import importlib
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import socketserver

# ZEWSFS MEMORY INJECTION - Dummy SFS2X to prevent import crashes
def inject_sfs_dummies():
    class DummyRoom:
        def __init__(self, *args, **kwargs):
            self.id = 1
            self.name = "Plant Island"
            self.users = []
        def getId(self): return self.id
        def getName(self): return self.name

    class DummyMessage:
        def __init__(self, *args, **kwargs):
            pass
        def getId(self): return 1
        def getContent(self): return {}

    sfs_mod = importlib.import_module('sys')
    if 'sfs2x' not in sys.modules:
        sys.modules['sfs2x'] = importlib.import_module('types').ModuleType('sfs2x')
    if 'sfs2x.core' not in sys.modules:
        sys.modules['sfs2x.core'] = importlib.import_module('types').ModuleType('sfs2x.core')
    if 'sfs2x.protocol' not in sys.modules:
        sys.modules['sfs2x.protocol'] = importlib.import_module('types').ModuleType('sfs2x.protocol')
    if 'sfs2x.transport' not in sys.modules:
        sys.modules['sfs2x.transport'] = importlib.import_module('types').ModuleType('sfs2x.transport')
    
    sys.modules['sfs2x.protocol'].Room = DummyRoom
    sys.modules['sfs2x.protocol'].Message = DummyMessage
    sys.modules['sfs2x.core'].Room = DummyRoom

inject_sfs_dummies()

# DB MANAGEMENT
DB_FILE = "users_db.json"

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def save_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"[DB ERROR] {e}")

# DEFAULT USER TEMPLATE
def create_default_user(bbb_id):
    return {
        "user_id": str(uuid.uuid4()),
        "bbb_id": bbb_id,
        "session_token": str(uuid.uuid4()),
        "diamonds": 50,
        "coins": 1000,
        "relics": 10,
        "prestige_level": 1,
        "islands": {
            "1": {  # Plant Island
                "name": "Plant Island",
                "monsters": [
                    {
                        "id": "MONSTER_A",
                        "name": "Noggin",
                        "level": 15,
                        "happiness": 100
                    }
                ]
            }
        },
        "monsters": ["MONSTER_A"]
    }

# HTTP HANDLER
class MSMHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Silence default logs

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path.strip("/")
        query_params = parse_qs(parsed_path.query)
        
        # Read body for POST
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = {}
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            if 'application/json' in self.headers.get('Content-Type', ''):
                try:
                    post_data = json.loads(body)
                except:
                    pass
            else:
                post_data = parse_qs(body)
                post_data = {k: v[0] if isinstance(v, list) else v for k, v in post_data.items()}

        # Merge query and post
        params = {}
        for d in [query_params, post_data]:
            for k, v in d.items():
                if isinstance(v, list):
                    params[k] = v[0] if v else ""
                else:
                    params[k] = v

        print(f"\n{'='*60}")
        print(f"REQUEST: {self.command} {self.path}")
        print(f"PARAMS: {params}")
        
        response = {"status": "error", "msg": "unknown_endpoint"}
        status_code = 200

        db = load_db()

        # HEALTH
        if path == "" or path == "health" or path.endswith("health"):
            response = {"status": "success", "msg": "MSM_SERVER_ALIVE"}
        
        # LOGIN
        elif "login" in path.lower() or path.endswith("login_user.php"):
            bbb_id = params.get("bbb_id") or params.get("id") or "guest_" + str(int(time.time()))
            if bbb_id not in db:
                db[bbb_id] = create_default_user(bbb_id)
                save_db(db)
            
            user = db[bbb_id]
            response = {
                "user_id": user["user_id"],
                "session_token": user["session_token"],
                "diamonds": user["diamonds"],
                "coins": user["coins"],
                "relics": user["relics"],
                "status": "success"
            }
        
        # GET USER
        elif "get_user" in path.lower() or "g_u_d" in path.lower():
            bbb_id = params.get("bbb_id") or list(db.keys())[0] if db else "guest"
            if bbb_id not in db:
                db[bbb_id] = create_default_user(bbb_id)
                save_db(db)
            user = db[bbb_id]
            response = {
                "user": user,
                "islands": user.get("islands", {}),
                "status": "success"
            }
        
        # SUBMIT ACTION
        elif "submit_action" in path.lower() or "action" in path.lower():
            bbb_id = params.get("bbb_id") or "guest"
            cmd = params.get("cmd", "")
            
            if bbb_id not in db:
                db[bbb_id] = create_default_user(bbb_id)
            
            user = db[bbb_id]
            
            if cmd == "b_m":  # Breed Monsters
                rare_chance = 0.15  # v5.4.2 event simulation
                is_rare = time.time() % 10 < 1.5  # Temporal probability
                
                if is_rare and user["diamonds"] >= 10:
                    user["diamonds"] -= 10
                    monster = "MONSTERRARE_FLASQUE_v542"
                    response["rare_trigger"] = True
                else:
                    monster = "MONSTER_NOGGIN"
                    response["rare_trigger"] = False
                
                if "monsters" not in user:
                    user["monsters"] = []
                user["monsters"].append(monster)
                
                # Add to island
                if "1" in user.get("islands", {}):
                    user["islands"]["1"]["monsters"].append({
                        "id": monster,
                        "name": monster.replace("_", " ").title(),
                        "level": 1,
                        "happiness": 80
                    })
                
                response["monster_added"] = monster
                response["diamonds"] = user["diamonds"]
            
            elif cmd == "c_b_p":  # Clubbox Prestige
                user["prestige_level"] = user.get("prestige_level", 1) + 1
                response["prestige_level"] = user["prestige_level"]
                response["stickers"] = ["sticker_summer_2026_01"]
            
            save_db(db)
            response["status"] = "success"
        
        print(f"RESPONSE: {response}")
        print(f"{'='*60}\n")
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

# SERVER
def run_server():
    port = int(os.environ.get("PORT", 9933))
    server_address = ('0.0.0.0', port)
    
    # Use ThreadingHTTPServer for better concurrency
    httpd = socketserver.ThreadingTCPServer(server_address, MSMHandler)
    
    print(f"MSM v5.4.2 Emulated Backend started on http://0.0.0.0:{port}")
    print("Railway Healthcheck compatible | Persistent JSON DB active")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
