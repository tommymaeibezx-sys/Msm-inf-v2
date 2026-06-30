# ==============================================================================
# REPLICA BACKEND MSM (v5.4.2) - SERVIDOR API HTTP CATCH-ALL PARA RAILWAY
# Guardar como: server.py
# ==============================================================================

import time
import sys
import os
import asyncio
import json
import types
import importlib

# 1. Configurar y asegurar rutas de ejecución en el contenedor de Railway
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

class DummyRoom:
    pass

try:
    sys.modules['sfs2x.protocol'] = importlib.import_module('sfs2x.protocol')
    setattr(sys.modules['sfs2x.protocol'], 'Room', DummyRoom)
except Exception:
    pass

from sfs2x.core import SFSObject
from sfs2x.protocol import Message
from sfs2x.transport import TCPAcceptor

# ==============================================================================
# MOTORES LÓGICOS DEL BACKEND API HTTP
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

    def log_separator(self, title):
        print(f"\n{'-'*30} {title} {'-'*30}")

    async def on_client_message(self, client_session, message: "Message"):
        pass 

    async def handle_http_request(self, writer, raw_request: str):
        """
        Enrutador API HTTP Catch-All. Responde con éxito a CUALQUIER sub-ruta
        que pida el juego y la imprime en los logs para su análisis.
        """
        lines = raw_request.split("\r\n")
        first_line = lines[0] if lines else ""
        
        # Omitir peticiones basura del navegador como el favicon para limpiar logs
        if "favicon.ico" in first_line:
            writer.close()
            await writer.wait_closed()
            return

        self.log_separator("PETICIÓN API HTTP DETECTADA")
        print(f"[Request Line]: {first_line}")

        # Extraer la ruta exacta solicitada por el APK
        parts = first_line.split(" ")
        path = parts[1] if len(parts) > 1 else "/"
        print(f"[Ruta Solicitada por APK]: {path}")

        # JSON de Respuesta Universal Exitoso de My Singing Monsters v5.4.2
        response_data = {
            "status": "success",
            "server_time": int(time.time()),
            "user_id": 84629473,
            "session_token": "msm_http_token_v542",
            "diamonds": 9999,
            "coins": 5000000,
            "relics": 500,
            "maintenance": False,
            "islands": [
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
        }

        # Construir la respuesta con las cabeceras HTTP estándar
        body = json.dumps(response_data, indent=2)
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
        print(f"[<- Respondido] : Datos de inicio e islas inyectados para la ruta: {path}")

    async def handle_hybrid_connection(self, reader, writer):
        try:
            data = await reader.read(4096)
            if not data:
                return

            raw_request = data.decode('utf-8', errors='ignore')
            await self.handle_http_request(writer, raw_request)
                
        except Exception as e:
            print(f"[-] Error en el canal de la API: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        self.log_separator("INICIALIZACIÓN DEL BACKEND API HTTP")
        try:
            raw_server = await asyncio.start_server(self.handle_hybrid_connection, self.host, self.port)
            self.log_separator("✓ API HTTP ONLINE EN RAILWAY")
            print(f"[✓] Servidor Catch-All escuchando activamente en el puerto: {self.port}")
            
            async with raw_server:
                await raw_server.serve_forever()
        except Exception as fatal_err:
            print(f"[-] Error fatal de red en la API: {fatal_err}")
            return

if __name__ == "__main__":
    PORT_SELECCIONADO = int(os.environ.get("PORT", 9933))
    server = MsmZewServer(host="0.0.0.0", port=PORT_SELECCIONADO)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n[-] Servidor apagado.")
