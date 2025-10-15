from pathlib import Path
from handlers import register
from protocol import Message, MessageType, Image, load_pngs_as_b64

@register(MessageType.SHOWSTART)
async def handle_SHOWSTART(ws, *, numbers, texts, assets_dir: Path) -> Message:
    pngs = ["Start.png"]
    return Message(
        messagetype=MessageType.SHOWSTART,
        numbers=numbers,
        texts=texts,
        images=[
            Image(
                name="start", text="", font="Arial", fontsize=14, textcolor="#000",
                x=0, y=0, w=1200, h=700, filename="Start.png"
            ),
        ],
        rectangles=[], triangles=[], arrows=[],
        png_payloads=load_pngs_as_b64(assets_dir, pngs),
    )
