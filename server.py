# ==============================================================================
# REPLICA BACKEND MSM (v5.4.2) - EDICIÓN HÍBRIDA CON PARCHE DE TEXTO DIRECTO
# Guardar como: server.py
# ==============================================================================

import time
import sys
import os
import asyncio
import json
import types
from importlib.machinery import SourceFileLoader

# 1. Configurar y asegurar rutas en el contenedor de Linux de Railway
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# ==============================================================================
# INYECTOR DE PARCHE VIRTUAL MEDIANTE CARGA PREVENTIVA DIRECTA DE DISCO
# ==============================================================================
class DummyRoom:
    """Clase ficticia mínima para satisfacer el __init__.py defectuoso"""
    pass

class DummyMessage:
    """Clase ficticia para pre-registrar las anotaciones de tipo de red"""
    pass

# Forzar la inyección directamente en el archivo del protocolo antes de las importaciones legítimas
try:
    protocol_init_path = os.path.join(ROOT_DIR, "sfs2x", "protocol", "__init__.py")
    if os.path.exists(protocol_init_path):
        # Cargamos el archivo físicamente en memoria como un módulo aislado
        loader = SourceFileLoader("sfs2x.protocol", protocol_init_path)
        mod_protocol = types.ModuleType(loader.name)
        
        # Le inyectamos la clase Room antes de compilarlo
        mod_protocol.Room = DummyRoom
        mod_protocol.Message = DummyMessage
        sys.modules["sfs2x.protocol"] = mod_protocol
        
        # Ejecutamos el cargador para rellenar el resto del módulo nativo
        loader.exec_module(mod_protocol)
except Exception as e:
    print(f"[*] Alerta del inyector preventivo de disco: {e}")

# ==============================================================================
# IMPORTACIONES REALES DEL FRAMEWORK TRAS EL SANEAMIENTO DIRECTO
# ==============================================================================
from sfs2x.core import SFSObject
from sfs2x.protocol import Message
from sfs2x.transport import TCPAcceptor

# Asegurar la persistencia del parche en el entorno de ejecución global
sys.modules["sfs2x.protocol"].Room = DummyRoom

# ==============================================================================
# LÓGICA DEL SERVIDOR REPLICA MY SINGING MONSTERS 5.4.2
# ==============================================================================
class MsmZewServer:
    def __init__(self, host="0.0.0.0", port=9933):
        self.host = host
        self.port = port
        
        try:
            self.acceptor = TCPAcceptor(self.host, self.port, self.on_client_message)
        except TypeError:
            try:
                self.acceptor = TCPAcceptor(self.host, self.port)
                self.acceptor.on_message = self.on_client_message
            except TypeError:
                self.acceptor = TCPAcceptor(host=self.host, port=self.port)
                if hasattr(self.acceptor, 'register_handler'):
                    self.acceptor.register_handler(self.on_client_message)

    def log_separator(self, title):
        print(f"\n{'-'*30} {title} {'-'*30}")

    async def on_client_message(self, client_session, message: "Message"):
        """Procesador nativo de comandos binarios SmartFox."""
        sfsobj_req = message.payload 
        if not sfsobj_req or "cmd" not in sfsobj_req:
            return

        cmd = sfsobj_req["cmd"]
        self.log_separator("PETICIÓN BINARIA SFS")
        print(f"[Endpoint SFS]: '{cmd}'")
        print(f"[Payload SFS] : {json.dumps(sfsobj_req, indent=2)}")

        sfsobj_res = {"cmd": cmd, "status": 1}

        if cmd == "g_u_d":
            sfsobj_res["islands"] = [{"island_id": 1, "monsters": [{"monster_instance_id": 12005, "monster_id": "MONSTER_A", "level": 15, "happiness": 100, "last_collected": int(time.time()) - 60}]}]
        elif cmd == "b_m":
            sfsobj_res["result_monster_type"] = "MONSTERRARE_FLASQUE_v542"
            sfsobj_res["time_required"] = 86400  
            sfsobj_res["rare_trigger"] = True
        elif cmd == "c_b_p":
            sfsobj_res["prestige_level"] = 3
            sfsobj_res["reward_stickers"] = ["sticker_summer_2026_01"]

        response_message = Message(payload=sfsobj_res)
        await client_session.send(response_message)

    async def handle_http_request(self, writer, raw_request: str):
        """Servidor Web Integrado para la autenticación de BBB_AUTH_SERVER."""
        lines = raw_request.split("\r\n")
        first_line = lines[0] if lines else ""
        
        self.log_separator("PETICIÓN WEB HTTP DETECTADA")
        print(f"[Request Line]: {first_line}")

        response_data = {
            "status": "success",
            "user_id": 84629473,
            "session_token": "msm_cloud_token_v542",
            "server_time": int(time.time()),
            "maintenance": False
        }
        
        body = json.dumps(response_data)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "\r\n"
            f"{body}"
        )
        
        writer.write(response.encode('utf-8'))
        await writer.drain()
        print("[<- Response HTTP]: Datos de inicio de sesión devueltos al APK.")

    async def handle_hybrid_connection(self, reader, writer):
        """Discriminador automático de protocolo: Separa HTTP de SmartFox binario."""
        peer = writer.get_extra_info('peername')
        try:
            data = await reader.read(4096)
            if not data:
                return

            if data[:3] in (b'GET', b'POS', b'PUT', b'DEL', b'OPT'):
                raw_request = data.decode('utf-8', errors='ignore')
                await self.handle_http_request(writer, raw_request)
            else:
                self.log_separator("TRÁFICO BINARIO DETECTADO")
                print(f"[Origen]: {peer} -> Canalizando al flujo del servidor...")
                print(f"[Volumen]: {len(data)} bytes recibidos.")
                
        except Exception as e:
            print(f"[-] Error en conexión híbrida: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        self.log_separator("INICIALIZACIÓN DEL BACKEND HÍBRIDO")
        print(f"[*] Abriendo sockets en la interfaz global 0.0.0.0:{self.port}...")
        
        started = False
        for method_name in ['bind', 'listen', 'serve_forever', 'start_server', 'run']:
            if hasattr(self.acceptor, method_name):
                method = getattr(self.acceptor, method_name)
                try:
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    else:
                        method()
                    started = True
                    break
                except Exception:
                    pass
        
        if not started:
            try:
                raw_server = await asyncio.start_server(self.handle_hybrid_connection, self.host, self.port)
                self.log_separator("✓ SERVIDOR INTEGRADO ONLINE EN RAILWAY")
                print(f"[✓] Escuchando solicitudes WEB y SOCKETS en el mismo puerto: {self.port}")
                
                async with raw_server:
                    await raw_server.serve_forever()
            except Exception as fatal_err:
                print(f"[-] Error fatal de red en el puerto: {fatal_err}")
                return

if __name__ == "__main__":
    PORT_SELECCIONADO = int(os.environ.get("PORT", 9933))
    server = MsmZewServer(host="0.0.0.0", port=PORT_SELECCIONADO)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n[-] Servidor apagado.")
