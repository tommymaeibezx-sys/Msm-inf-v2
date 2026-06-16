import asyncio
import os
import json

# Importaciones oficiales de la arquitectura de ZewSFS que viste en la imagen
from sfs2x.transport import server_from_url, TCPTransport
from sfs2x.protocol import Message, ControllerID, SysAction
from sfs2x.core import SFSObject

PORT = int(os.environ.get("PORT", 9933))
BIND_URL = f"tcp://0.0.0.0:{PORT}"
DB_FILE = "player_database.json"

# --- BASE DE DATOS DIOS: NIVEL 67 Y RECURSOS MÁXIMOS ---
GOD_PLAYER_TEMPLATE = {
    "userId": 77777,
    "username": "ZewSFS_God_Player",
    "coins": 999999999,
    "diamonds": 999999999,
    "food": 999999999,
    "level": 67,
    "xp": 50000000,
    "islands": {
        "1": {"name": "Plant Island", "unlocked": True, "monsters": [], "nursery": []},
        "2": {"name": "Cold Island", "unlocked": True, "monsters": [], "nursery": []},
        "3": {"name": "Air Island", "unlocked": True, "monsters": [], "nursery": []},
        "4": {"name": "Water Island", "unlocked": True, "monsters": [], "nursery": []},
        "5": {"name": "Earth Island", "unlocked": True, "monsters": [], "nursery": []}
    }
}

def load_or_create_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump(GOD_PLAYER_TEMPLATE, f, indent=4)
        return GOD_PLAYER_TEMPLATE
    with open(DB_FILE, "r") as f:
        return json.load(f)

# --- PROCESADOR DE ACCIONES SMARTFOX (MSM EXTENSION) ---
def process_msm_command(cmd: str, req_payload: SFSObject) -> SFSObject:
    player = load_or_create_db()
    res_payload = SFSObject()
    
    # "g_ud" es el comando nativo abreviado de My Singing Monsters para cargar el usuario
    if cmd == "g_ud":
        res_payload.put_utf_string("status", "success")
        res_payload.put_int("level", player["level"])
        res_payload.put_int("coins", player["coins"])
        res_payload.put_int("diamonds", player["diamonds"])
        res_payload.put_utf_string("player_json", json.dumps(player))
        return res_payload

    # Respuesta de respaldo por defecto para mantener estable la red
    res_payload.put_utf_string("status", "success")
    return res_payload

# --- CONTROLADOR CENTRAL DEL CLIENTE ---
async def handle_client(client: TCPTransport):
    addr = f"{client.host}:{client.port}"
    print(f"[🟢] Dispositivo conectado al emulador: {addr}")
    
    try:
        async for message in client.listen():
            req_payload = message.payload
            
            # Identificamos el comando de la trama recibida
            cmd = "g_ud"
            if req_payload and hasattr(req_payload, 'get_utf_string'):
                try:
                    cmd = req_payload.get_utf_string("cmd")
                except:
                    cmd = "g_ud"
            
            print(f"[⚙️] Procesando comando en ZewSFS: '{cmd}'")
            response_payload = process_msm_command(cmd, req_payload)
            
            # Respondemos utilizando el formato de mensajes del framework
            await client.send(Message(
                controller=ControllerID.SYSTEM,
                action=SysAction.PUBLIC_MESSAGE,
                payload=response_payload
            ))
            
    except Exception as e:
        print(f"[🔴] Error o desconexión con {addr}: {e}")
    finally:
        print(f"[⚪] Sesión SFS finalizada para {addr}")

# --- ARRANQUE PRINCIPAL DEL SERVIDOR ---
async def run_server():
    load_or_create_db() # Prepara la base de datos chetada antes de encender el puerto
    print(f"🚀 Emulador MSM ZewSFS Activo. Escuchando en {BIND_URL}")
    
    async for client in server_from_url(BIND_URL):
        asyncio.create_task(handle_client(client))

if __name__ == "__main__":
    asyncio.run(run_server())
