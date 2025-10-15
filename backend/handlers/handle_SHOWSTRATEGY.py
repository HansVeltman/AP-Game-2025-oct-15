from pathlib import Path
from handlers import register
from protocol import Message, MessageType, Image, Rectangle, LineType, load_pngs_as_b64

@register(MessageType.SHOWSTRATEGY)
async def handle_SHOWSTRATEGY(ws, *, numbers, texts, assets_dir: Path) -> Message:
    pngs = ["Strategy.png"]
    return Message(
        messagetype=MessageType.SHOWSTRATEGY,
        numbers=numbers,
        texts=texts,
        images=[
            Image(
                name="strategy", text="", font="Arial", fontsize=14, textcolor="#000",
                x=4, y=4, w=1200, h=700, filename="Strategy.png"
            ),
        ],
        triangles=[], arrows=[],
        png_payloads=load_pngs_as_b64(assets_dir, pngs),
    )
