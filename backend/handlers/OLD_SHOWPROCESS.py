from pathlib import Path
from handlers import register
from protocol import Message, MessageType, Triangle, LineType


@register(MessageType.SHOWPROCESS)
async def handle_SHOWPROCESS(ws, *, numbers, texts, assets_dir: Path) -> Message:
    tris = [Triangle(name="proc", text="Process", font="Arial", fontsize=14, textcolor="#000", x=120, y=120, w=140, h=100, linewidth=2, fill="#eef", stroke="#55f", linetype=LineType.SOLID)]
    return Message(messagetype=MessageType.SHOWPROCESS, numbers=numbers, texts=texts, images=[], rectangles=[], triangles=tris, arrows=[], png_payloads={})

