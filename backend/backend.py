# backend/backend.py
import asyncio
import json
import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional, Tuple, List

import websockets
from websockets.server import WebSocketServerProtocol

from protocol import MessageType
from handlers import registry  # side-effect imports register handlers
from protocol import Message

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("backend")

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"  # statische afbeeldingen/PNG's

# ---------- core dispatcher ----------
async def handle_text_message(text: str, *, ws: Optional[WebSocketServerProtocol]=None) -> str:
    """
    Houd deze functie *dun*:
      a) JSON parsen → messagetype ophalen
      b) handler opzoeken → aanroepen met payload
      c) antwoord (Message) serialiseren → terugsturen
    """
    # a) JSON parsen
    try:
       msg = json.loads(text)
    except json.JSONDecodeError:
       return json.dumps({"type": "echo", "data": text})

    # ping/pong blijft handig
    if (msg.get("type") or "").lower() == "ping":
        return json.dumps({"type": "pong"})

    # b) messagetype ophalen
    mt_raw = msg.get("messagetype")
    if not mt_raw:
        return json.dumps({"type": "error", "error": "missing 'messagetype'"})
    try:
        mtype = MessageType(mt_raw)
    except Exception:
        return json.dumps({"type": "error", "error": f"unknown messagetype: {mt_raw}"})

    # handler opzoeken
    handler = registry.get(mtype)
    if not handler:
        return json.dumps({"type": "error", "error": f"no handler registered for {mtype.value}"})

    numbers = msg.get("numbers") or []
    texts = msg.get("texts") or []

    # c) handler aanroepen + serialiseren
    try:
        response: Message = await handler(ws, numbers=numbers, texts=texts, assets_dir=ASSETS_DIR)
        return json.dumps(response.to_jsonable())
    except Exception as e:
        log.exception("handler %s failed", mtype.value)
        return json.dumps({"type":"error","error": str(e)})

# ---------- websocket loop ----------
async def handler(ws: WebSocketServerProtocol):
    log.info("client connected: %s path=%s", ws.remote_address, getattr(ws, "path", ""))
    try:
        async for raw in ws:
            if isinstance(raw, (bytes, bytearray, memoryview)):
                # we ondersteunen geen binaire frames in deze build
                log.warning("binary frame received (ignored)")
                continue
            text = str(raw)
            snippet = (text[:300] + "...") if len(text) > 300 else text
            log.info("WS recv: %s", snippet)
            reply = await handle_text_message(text, ws=ws)
            r_snip = (reply[:300] + "...") if len(reply) > 300 else reply
            log.info("WS send: %s", r_snip)
            await ws.send(reply)
    except websockets.ConnectionClosed:
        pass
    finally:
        log.info("client disconnected: %s", ws.remote_address)

# ---------- kleine HTTP routes (assets + healthz) ----------
def _http_response(status: int, body: bytes, content_type: str = "text/plain; charset=utf-8",
                   headers: Optional[List[Tuple[str,str]]] = None):
    hs = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "public, max-age=86400"),
    ]
    if headers:
        hs.extend(headers)
    return (status, hs, body)

async def process_request(path: str, request_headers) -> Optional[Tuple[int, List[Tuple[str, str]], bytes]]:
    # health endpoint
    if path == "/healthz":
        return _http_response(200, b"OK")

    # serve static assets under /assets/<filename>
    if path.startswith("/assets/"):
        rel = path[len("/assets/"):].lstrip("/")
        safe = rel.replace("..","").replace("\\","/")  # basic path sanitization
        f = (ASSETS_DIR / safe).resolve()
        try:
            if not str(f).startswith(str(ASSETS_DIR.resolve())):
                return _http_response(403, b"Forbidden")
            data = f.read_bytes()
        except FileNotFoundError:
            return _http_response(404, b"Not Found")
        mime, _ = mimetypes.guess_type(f.name)
        return _http_response(200, data, mime or "application/octet-stream")

    # let websockets upgrade handle everything else (usually "/")
    return None

# ---------- main ----------
async def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8765"))
    server = await websockets.serve(
        handler,
        host,
        port,
        max_size=20_000_000,
        process_request=process_request,
    )
    log.info("WS-server listening on ws://%s:%s", host, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
