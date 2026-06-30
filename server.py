# ==============================================================================
# REPLICA BACKEND MSM (v5.4.2) - SERVIDOR API HTTP PURO PARA BBB_AUTH_SERVER
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
        pass # Ignorado ya que el juego opera por HTTP puro en esta versión

    async def handle_http_request(self, writer, raw_request: str):
        """
        Enrutador API HTTP Avanzado. Captura la ruta que pide el juego 
        a través de BBB_AUTH_SERVER y le devuelve el JSON correcto.
        """
        lines = raw_request.split("\r\n")
        first_line = lines[0] if lines else ""
        
        self.log_separator("PETICIÓN API HTTP DETECTADA")
        print(f"[Request Line]: {first_line}")

        # Identificar la ruta (endpoint) solicitada por el cliente de MSM
        parts = first_line.split(" ")
        path = parts[1] if len(parts) > 1 else "/"
        
        print(f"[Ruta Pedida] : {path}")

        # Inicializar el contenedor base de respuesta JSON
        response_data = {"status": "success", "server_time": int(time.time())}

        # --------------------------------======================================
        # ENRUTADOR DE RUTAS WEB (ENDPOINTS HTTP MSM v5.4.2)
        # --------------------------------======================================
        if "login" in path or "auth" in path or path == "/":
            # --- Endpoint de Inicio de Sesión ---
            response_data.update({
                "user_id": 84629473,
                "session_token": "msm_http_token_v542",
                "diamonds": 9999,
                "coins": 5000000,
                "relics": 500,
                "maintenance": False
            })
            print("[Acción]      : Procesando Autenticación de Usuario.")

        elif "g_u_d" in path or "user_data" in path or "islands" in path:
            # --- Endpoint para Cargar el Estado de las Islas ---
            response_data["islands"] = [
                {
                    "island_id": 1, # Isla de Planta
                    "monsters": [
                        {
                            "monster_instance_id": 12005,
                            "monster_id": "MONSTER_A", # Noggin
                            "level": 15,
                            "happiness": 100,
                            "last_collected": int(time.time()) - 60
                        }
                    ]
                }
            ]
            print("[Acción]      : Cargando Estructuras e Islas del Jugador v5.4.2.")

        elif "b_m" in path or "breed" in path:
            # --- Endpoint de Cruce de Criaturas (Evento Rare Flasque de la 5.4.2) ---
            response_data.update({
                "result_monster_type": "MONSTERRARE_FLASQUE_v542",
                "time_required": 86400,
                "rare_trigger": True
            })
            print("[Acción]      : Ejecutando Cruce Automático de Monstruo Raro.")

        elif "c_b_p" in path or "prestige" in path:
            # --- Endpoint de Prestigio de Estructuras v5.4.2 ---
            response_data.update({
                "prestige_level": 3,
                "reward_stickers": ["sticker_summer_2026_01"]
            })
            print("[Acción]      : Actualizando Prestigio del Clubbox.")

        else:
            # Fallback genérico para cualquier otra ruta de la API
            response_data["msg"] = "MSM_HTTP_ENDPOINT_OK"

        # Construir la respuesta con las cabeceras HTTP estándar de Railway
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
        print(f"[<- Response] : JSON enviado de vuelta al APK:\n{body}")

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
        print(f"[*] Abriendo sockets en la interfaz global 0.0.0.0:{self.port}...")
        
        try:
            # Levantamos el servidor HTTP asíncrono puro sobre el puerto asignado
            raw_server = await asyncio.start_server(self.handle_hybrid_connection, self.host, self.port)
            self.log_separator("✓ API HTTP ONLINE EN RAILWAY")
            print(f"[✓] Servidor de endpoints escuchando peticiones en el puerto: {self.port}")
            
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
