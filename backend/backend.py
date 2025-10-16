# backend/backend.py
import asyncio
import logging
import os
from typing import Optional, Tuple, List

import websockets
from websockets.server import WebSocketServerProtocol

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
log = logging.getLogger("alignment-backend")

# ---------- message handling ----------
async def handle_message(text: str) -> str:
    """
    Verwerk een binnenkomend bericht (als tekst) en geef tekst terug.
    Vervang dit met jouw eigen logica.
    """
    # Voorbeeld: echo met prefix
    return f"server: {text}"

# ---------- websocket handler ----------
async def handler(ws: WebSocketServerProtocol):
    log.info("client connected: %s", ws.remote_address)
    try:
        async for raw in ws:
            # raw kan str of bytes/memoryview zijn → normaliseren naar str
            if isinstance(raw, (bytes, bytearray, memoryview)):
                data = bytes(raw).decode("utf-8", errors="replace")
            else:
                data = str(raw)

            reply = await handle_message(data)
            await ws.send(reply)
    except websockets.ConnectionClosedOK:
        pass
    except websockets.ConnectionClosedError as e:
        log.warning("connection closed with error: %s", e)
    finally:
        log.info("client disconnected: %s", ws.remote_address)

async def process_request(path: str, request_headers) -> Optional[Tuple[int, List[Tuple[str, str]], bytes]]:
    if path == "/healthz":
        body = (b"OK" if path == "/healthz"
                else b"Alignment WebSocket server. Connect with a WebSocket client.")
        headers = [("Content-Type", "text/plain; charset=utf-8"),
                   ("Content-Length", str(len(body))),
                   ("Cache-Control", "no-cache")]
        return (200, headers, body)
    return None  # anders: laat de WS-upgrade doorgaan

async def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8765"))
    server = await websockets.serve(
        handler, host, port, max_size=10_000_000, process_request=process_request
    )
    log.info("WS-server listening on ws://%s:%s", host, port)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
