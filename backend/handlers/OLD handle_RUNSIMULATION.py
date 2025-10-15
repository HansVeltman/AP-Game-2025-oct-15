from pathlib import Path
from handlers import register
from protocol import Message, MessageType


@register(MessageType.RUNSIMULATION)
async def handle_RUNSIMULATION(ws, *, numbers, texts, assets_dir: Path) -> Message:
# toekomstige sim-resultaten kunnen shapes/images vullen
    return Message(messagetype=MessageType.RUNSIMULATION, numbers=numbers, texts=["started", *texts], images=[], rectangles=[], triangles=[], arrows=[], png_payloads={})

