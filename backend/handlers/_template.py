from pathlib import Path
from protocol import Message, MessageType, Image, Rectangle, Triangle, Arrow, LineType, load_pngs_as_b64


async def handle(ws, *, numbers, texts, assets_dir: Path) -> Message:
    pngs = ["Start.png"]
    return Message(
        messagetype=MessageType.SHOWSTART,
        numbers=[1.0],
        texts=["ok"],
        images=[Image(name="start", text="", font="Arial", fontsize=14, textcolor="#000", x=20, y=20, w=600, h=400, filename="Start.png")],
        rectangles=[], triangles=[], arrows=[],
        png_payloads=load_pngs_as_b64(assets_dir, pngs)
    )