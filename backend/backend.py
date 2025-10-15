import asyncio, json, logging, websockets
from pathlib import Path
from websockets.server import WebSocketServerProtocol
from protocol import Message, MessageType
from handlers import registry # mapping: MessageType -> callable

ASSETS_DIR = Path(__file__).parent / "assets"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
log = logging.getLogger("ws")

def _truncate(s, n=500):  # for logging
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f"... ({len(s)-n} more)"


async def handle_message(ws: WebSocketServerProtocol, data: str, peer: str | tuple | None) -> None:
    try:
        payload = json.loads(data)
        mtype = MessageType(payload.get("messagetype"))
        numbers = payload.get("numbers", [])
        texts = payload.get("texts", [])
        log.info("RX from %s ", _truncate(data))
    except Exception as exc:
        err = {"error": f"invalid message: {exc}"}
        await ws.send(json.dumps(err))
        log.warning("TX to %s: %s", peer, _truncate(err))
        return

    handler = registry.get(mtype)  # searches in the register for the right handler, dep on mtype
    if not handler:  # no handler found
        await ws.send(json.dumps({"error": f"no handler for {mtype}"}))
        log.info({"error": f"no handler for {mtype}"})
        return

    # Handler bouwt een Message (back→front) en stuurt die terug
    reply = await handler(ws, numbers=numbers, texts=texts, assets_dir=ASSETS_DIR)

    # Laat handlers dict/list/str of Message mogen teruggeven:
    if isinstance(reply, str):
        resp_text = reply  # al een JSON-string (handler heeft zelf gedumpt)
        log_payload = reply  # voor logging
    elif isinstance(reply, (dict, list)):
        resp_text = json.dumps(reply, ensure_ascii=False)  # JSON-serialiseerbare payload
        log_payload = reply
    else:
        # assumeert jouw bestaande Message-type met .to_jsonable()
        resp_text = json.dumps(reply.to_jsonable(), ensure_ascii=False)
        log_payload = reply.to_jsonable()

    await ws.send(resp_text)
    log.info("TX to %s: %s", peer, _truncate(log_payload))

async def handler(ws: WebSocketServerProtocol):
    print("Client verbonden")
    peer = ws.remote_address  # (host, port)
    log.info("Client connected: %s", peer)

    try:
        async for msg in ws:
            if isinstance(msg, (bytes, bytearray)):
                err = {"error": "binary not supported"}
                await ws.send(json.dumps(err))
                log.warning("RX (binary %d bytes) from %s; %s; %s", len(msg), peer, _truncate(err))
                continue
            # Verwerk elk bericht meteen (niet pas na de loop!)
            await handle_message(ws, msg, peer)
        
    except websockets.exceptions.ConnectionClosedOK:
        log.info("Client closed: %s", peer)
    except websockets.exceptions.ConnectionClosedError as e:
        log.warning("Client error/closed: %s (%s)", peer, e)
    except Exception:
        log.exception("Unhandled error for %s", peer)

async def main():
    async with websockets.serve(handler, "localhost", 8765, max_size=10_000_000):
        log.info("WS-server listening on ws://localhost:8765")
        try:
            await asyncio.Future()  # draai “voor altijd” tot we onderbroken worden
        except asyncio.CancelledError:  # onderdruk de traceback bij annuleren
            pass
        finally:
            log.info("WS-Backend server shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:  # onderdruk de traceback bij Ctrl+C
        print("\n Interrupted — bye!")


