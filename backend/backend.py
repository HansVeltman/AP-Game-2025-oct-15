# backend/backend.py
import asyncio
import logging
import os
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List, Union

import websockets
from websockets.server import WebSocketServerProtocol

# Protocol / Handlers
from protocol import MessageType, Message
from handlers import registry  # central registry: MessageType -> async handler

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
log = logging.getLogger("alignment-backend")

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"  # afbeeldingen voor asset-requests

# ---------- helpers ----------
def read_asset_b64(name: str):
    """Lees een asset uit backend/assets en geef (data_b64, mime) terug."""
    f = (ASSETS_DIR / name)
    # sandboxing: geen path traversal
    if not str(f.resolve()).startswith(str(ASSETS_DIR.resolve())):
        raise FileNotFoundError("forbidden path")
    data = f.read_bytes()
    mime, _ = mimetypes.guess_type(f.name)
    return base64.b64encode(data).decode("ascii"), (mime or "application/octet-stream")

# ---------- message handling ----------
async def handle_text_message(text: str, *, ws: Optional[WebSocketServerProtocol]=None) -> str:
    """DUNNE DISPATCH:
    a) JSON parsen → messagetype ophalen
    b) handler opzoeken → aanroepen met payload
    c) antwoord serialiseren → JSON string terug
    Overige: ping/asset blijven hier voor eenvoud.
    """
    # 1) JSON parse
    try:
        msg = json.loads(text)
    except json.JSONDecodeError:
        return json.dumps({"type": "error", "error": "invalid json"})

    # 2) eenvoudige non-game types
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

    # 3) Centrale dispatch voor game messages
    mt_raw = msg.get("messagetype")
    if not mt_raw:
        return json.dumps({"type": "error", "error": "missing messagetype"})
    try:
        mt = MessageType(mt_raw)
    except Exception:
        return json.dumps({"type": "error", "error": f"unknown messagetype: {mt_raw}"})

    handler = registry.get(mt)
    if not handler:
        return json.dumps({"type": "error", "error": f"no handler for messagetype: {mt.value}"})

    # Payload (conventies)
    numbers = msg.get("numbers") or []
    texts = msg.get("texts") or []

    # 4) Execute handler with strict error boundary
    try:
        result = await handler(ws, numbers=numbers, texts=texts, assets_dir=ASSETS_DIR)
    except Exception as e:
        log.exception("handler %s crashed", mt.value)
        return json.dumps({"type": "error", "error": f"handler error in {mt.value}: {e}"})

    # 5) Serialize (zonder .to_json referentie)
    if isinstance(result, Message):
        # Message uit protocol.py heeft to_jsonable()
        try:
            return json.dumps(result.to_jsonable())
        except Exception:
            # Fallback: serialize dataclass
            from dataclasses import asdict
            return json.dumps(asdict(result))
    elif isinstance(result, dict):
        # Legacy handlers die al een jsonable dict teruggeven
        return json.dumps(result)
    else:
        return json.dumps({"type": "error", "error": f"invalid handler return for {mt.value}"})



# ---------- WS server ----------
async def handler(ws: WebSocketServerProtocol):
    log.info("client connected: %s", ws.remote_address)
    try:
        async for message in ws:
            if isinstance(message, bytes):
                # bytes: niet ondersteund
                await ws.send(json.dumps({"type": "error", "error": "binary frames not supported"}))
                continue

           # log compacte sample (max 300 chars), type-safe
            if isinstance(message, (bytes, bytearray, memoryview)):
                # binary frames zijn niet ondersteund; stuur fout en ga door
                await ws.send(json.dumps({"type": "error", "error": "binary frames not supported"}))
                continue

            msg_text: str = message  # nu gegarandeerd str voor de type-checker
            sample = (msg_text[:300] + "…") if len(msg_text) > 300 else msg_text
            log.info("<- %s", sample)

            resp = await handle_text_message(message, ws=ws)

            # Ook hier loggen we compact
            rsample = (resp[:300] + "…") if len(resp) > 300 else resp
            log.info("-> %s", rsample)

            await ws.send(resp)
    except websockets.ConnectionClosedOK:
        pass
    except websockets.ConnectionClosedError:
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
    # Alleen /healthz via HTTP; laat "/" vrij voor WS upgrade.
    if path == "/healthz":
        return _http_response(200, b"ok\n")
    return None

# ---------- main ----------
async def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8765"))
    server = await websockets.serve(
        handler,
        host,
        port,
        max_size=20_000_000,           # ~20 MB
        process_request=process_request,
    )
    log.info("WS-server listening on ws://%s:%s", host, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
