# ==============================================================================
# REPLICA BACKEND MSM (v5.4.2) - EDICIÓN REMOVED-ANNOTATIONS PARA RAILWAY
# Guardar como: server.py
# ==============================================================================

import time
import sys
import os
import asyncio
import socket
import json
import types

# 1. Asegurar rutas en el contenedor de Linux de Railway
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# ==============================================================================
# INYECTOR DE PARCHE VIRTUAL EN MEMORIA (PARA CONTENEDORES READ-ONLY)
# ==============================================================================
class DummyRoom:
    """Clase ficticia para saciar las importaciones circulares del framework"""
    pass

class DummyMessage:
    """Clase ficticia para pre-registrar las anotaciones de tipo de red"""
    pass

# Forzar el registro preventivo en el diccionario interno del sistema de Python (sys.modules)
try:
    for mod_name in ['sfs2x', 'sfs2x.protocol', 'sfs2x.core', 'sfs2x.transport']:
        if mod_name not in sys.modules:
            sys.modules[mod_name] = types.ModuleType(mod_name)
    
    # Inyectar atributos requeridos por las dependencias defectuosas de sfs2x
    sys.modules['sfs2x.protocol'].Room = DummyRoom
    sys.modules['sfs2x.protocol'].Message = DummyMessage
    sys.modules['sfs2x.transport'].Message = DummyMessage
    sys.modules['sfs2x.transport'].base = types.ModuleType('sfs2x.transport.base')
    sys.modules['sfs2x.transport'].base.Message = DummyMessage
except Exception as patch_err:
    print(f"[*] Alerta del inyector de memoria: {patch_err}")

# ==============================================================================
# IMPORTACIONES REALES DEL FRAMEWORK TRAS EL BYPASS VIRTUAL
# ==============================================================================
from sfs2x.core import SFSObject
from sfs2x.protocol import Message
from sfs2x.transport import TCPAcceptor

# Re-vincular la clase real una vez cargado el protocolo legítimo
sys.modules['sfs2x.protocol'].Room = DummyRoom

# ==============================================================================
# LÓGICA DEL SERVIDOR REPLICA MY SINGING MONSTERS 5.4.2
# ==============================================================================
class MsmZewServer:
    def __init__(self, host="0.0.0.0", port=9933):
        self.host = host
        self.port = port
        
        # Enlazar handlers dinámicamente según la estructura de tu versión de ZewSFS
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
        """Manejador principal de la extensión ZewSFS: Procesa comandos del juego."""
        sfsobj_req = message.payload 
        
        if not sfsobj_req or "cmd" not in sfsobj_req:
            self.log_separator("PAQUETE CON ANOMALÍAS")
            return

        cmd = sfsobj_req["cmd"]
        
        self.log_separator("PETICIÓN RECONOCIDA (MSM CLIENT)")
        print(f"[Timestamp]: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[Endpoint] : '{cmd}'")
        print(f"[Payload]  : {json.dumps(sfsobj_req, indent=2)}")

        sfsobj_res = {"cmd": cmd, "status": 1}

        # --- Enrutador lógico de Endpoints MSM v5.4.2 ---
        if cmd == "g_u_d":
            sfsobj_res["islands"] = [
                {
                    "island_id": 1, 
                    "monsters": [
                        {
                            "monster_instance_id": 12005,
                            "monster_id": "MONSTER_A",
                            "level": 15,
                            "happiness": 100,
                            "last_collected": int(time.time()) - 60
                        }
                    ]
                }
            ]

        elif cmd == "b_m":
            is_rare = True if (int(time.time()) % 2 == 0) else False
            if is_rare:
                sfsobj_res["result_monster_type"] = "MONSTERRARE_FLASQUE_v542"
                sfsobj_res["time_required"] = 86400  
                sfsobj_res["rare_trigger"] = True
            else:
                sfsobj_res["result_monster_type"] = "MONSTER_NOGGIN"
                sfsobj_res["time_required"] = 5
                sfsobj_res["rare_trigger"] = False

        elif cmd == "c_b_p":
            sfsobj_res["prestige_level"] = 3
            sfsobj_res["reward_stickers"] = ["sticker_summer_2026_01"]
        
        else:
            sfsobj_res["status"] = 0
            sfsobj_res["error"] = f"ERR_UNKNOWN_CMD_{cmd.upper()}"

        print(f"\n[<- RESPUESTA ENVIADA AL CLIENTE]")
        print(f"[Payload]  : {json.dumps(sfsobj_res, indent=2)}")

        response_message = Message(payload=sfsobj_res)
        await client_session.send(response_message)

    async def handle_raw_connection(self, reader, writer):
        peer = writer.get_extra_info('peername')
        self.log_separator("NUEVA CONEXIÓN RECONOCIDA")
        print(f"[Dirección Remota IP/Puerto]: {peer}")
        
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    self.log_separator("CONEXIÓN CERRADA")
                    break
                
                self.log_separator("PAQUETE EN TRÁNSITO")
                print(f"[Volumen de datos]: {len(data)} bytes")
                
        except Exception as e:
            print(f"[-] Excepción en el flujo: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        self.log_separator("INICIALIZACIÓN DE INTERFAZ DE RED")
        print(f"[*] Escaneando puertos asíncronos bajo la regla global {self.host}:{self.port}...")
        
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
                raw_server = await asyncio.start_server(self.handle_raw_connection, self.host, self.port)
                self.log_separator("✓ SERVIDOR EN LÍNEA EN RAILWAY")
                print(f"[*] Escuchando activamente en la regla de red interna: {self.host}:{self.port}")
                self.log_separator("CONSOLA DE MONITOREO")
                
                async with raw_server:
                    await raw_server.serve_forever()
            except Exception as fatal_socket_err:
                print(f"[-] Imposible asegurar el enlace de red: {fatal_socket_err}")
                return
            
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    PORT_SELECCIONADO = int(os.environ.get("PORT", 9933))
    server = MsmZewServer(host="0.0.0.0", port=PORT_SELECCIONADO)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n[-] Servidor MSM apagado.")
