# backend/backend.py
import asyncio
import logging
import os
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List

import websockets
from websockets.server import WebSocketServerProtocol

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
log = logging.getLogger("alignment-backend")

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"  # zet hier je afbeeldingen

# ---------- helpers ----------
def read_asset_b64(name: str):
    """Lees een asset uit backend/assets en geef (base64_string, mime_type) terug."""
    safe = name.lstrip("/").replace("\\", "/")
    f = (ASSETS_DIR / safe).resolve()
    if not str(f).startswith(str(ASSETS_DIR.resolve())):
        raise FileNotFoundError("forbidden path")
    data = f.read_bytes()
    mime, _ = mimetypes.guess_type(f.name)
    return base64.b64encode(data).decode("ascii"), (mime or "application/octet-stream")

# ---------- message handling ----------
async def handle_text_message(text: str) -> str:
    """
    Protocol (tekstframes met JSON):
    - {"type":"ping"} -> {"type":"pong"}
    - {"type":"asset","name":"Start.png"} ->
        {"type":"asset","name":"Start.png","mime":"image/png","data_b64":"..."}
    - {"messagetype": "...", ... } -> echo terug zodat je huidige frontend-debug blijft zien
    - anders -> {"type":"echo","data":...}
    """
    # 1) probeer JSON
    try:
        msg = json.loads(text)
    except json.JSONDecodeError:
        # geen JSON → simpele echo
        return json.dumps({"type": "echo", "data": text})

    # 2) gestandaardiseerde type-afhandeling
    t = (msg.get("type") or "").lower()
    if t == "ping":
        return json.dumps({"type": "pong"})

    if t == "asset":
        name = msg.get("name")
        if not name:
            return json.dumps({"type": "error", "error": "missing name"})
        try:
            b64, mime = read_asset_b64(name)
            return json.dumps({"type": "asset", "name": name, "mime": mime, "data_b64": b64})
        except FileNotFoundError:
            return json.dumps({"type": "error", "error": f"asset not found: {name}"})
        except Exception as e:
            log.exception("asset error")
            return json.dumps({"type": "error", "error": f"asset error: {e}"})

    # 3) behoud je bestaande 'messagetype'-flow als echo (voor debugging)
    if "messagetype" in msg:
        return json.dumps({"type": "echo", "data": msg})

    # 4) default echo
    return json.dumps({"type": "echo", "data": msg})

# ---------- websocket handler ----------
async def handler(ws: WebSocketServerProtocol):
    log.info("client connected: %s path=%s", ws.remote_address, getattr(ws, "path", ""))
    try:
        async for raw in ws:
            # Let op: binaire frames niet naar tekst decoderen (nu unsupported → skippen)
            if isinstance(raw, (bytes, bytearray, memoryview)):
                log.warning("binary frame received (ignored in this build)")
                continue

            text = str(raw)
            log.info("WS recv: %s", (text[:300] + "...") if len(text) > 300 else text)
            reply = await handle_text_message(text)
            log.info("WS send: %s", (reply[:300] + "...") if len(reply) > 300 else reply)
            await ws.send(reply)
    except websockets.ConnectionClosed:
        pass
    finally:
        log.info("client disconnected: %s", ws.remote_address)

# ---------- kleine HTTP health endpoint, WS-upgrade op "/" ----------
def _http_response(status: int, body: bytes, content_type: str = "text/plain; charset=utf-8"):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-cache"),
    ]
    return (status, headers, body)

async def process_request(path: str, request_headers) -> Optional[Tuple[int, List[Tuple[str, str]], bytes]]:
    # Alleen healthz via HTTP; laat "/" vrij voor WebSocket-upgrade
    if path == "/healthz":
        return _http_response(200, b"OK")
    return None

# ---------- main ----------
async def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8765"))
    server = await websockets.serve(
        handler,
        host,
        port,
        max_size=20_000_000,           # ~20 MB frames (ruimte ivm base64 overhead)
        process_request=process_request
    )
    log.info("WS-server listening on ws://%s:%s", host, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
