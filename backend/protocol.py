from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any
import base64


class LineType(str, Enum):
    SOLID = "SOLID"
    DASHED = "DASHED"
    DOTTED = "DOTTED"

class MessageType(str, Enum):
    SHOWSTART = "SHOWSTART"
    SHOWSTRATEGY = "SHOWSTRATEGY"
    SHOWPROCESS = "SHOWPROCESS"
    SHOWCONTROL = "SHOWCONTROL"
    SHOWORGANIZATION = "SHOWORGANIZATION"
    SHOWINFORMATION = "SHOWINFORMATION"
    RUNSIMULATION = "RUNSIMULATION"

@dataclass(frozen=True)
class Rectangle:
    name: str
    text: str
    font: str
    fontsize: int
    textcolor: str
    x: float
    y: float
    w: float
    h: float
    linewidth: int
    fill: str
    stroke: str
    linetype: LineType = LineType.SOLID


@dataclass(frozen=True)
class Triangle:
    name: str
    text: str
    font: str
    fontsize: int
    textcolor: str
    x: float
    y: float
    w: float
    h: float
    linewidth: int
    fill: str
    stroke: str
    linetype: LineType = LineType.SOLID

@dataclass(frozen=True)
class Arrow:
    name: str
    text: str
    font: str
    fontsize: int
    textcolor: str
    x1: float
    y1: float
    x2: float
    y2: float
    linewidth: int
    stroke: str
    linetype: LineType = LineType.SOLID
    arrow: float = 0.0 # pijlpuntlengte in px

@dataclass(frozen=True)
class Image:
    name: str
    text: str
    font: str
    fontsize: int
    textcolor: str
    x: float
    y: float
    w: float
    h: float
    filename: str # logische naam (ook sleutel voor caching)

@dataclass
class Message:
    messagetype: MessageType
    numbers: List[float]
    texts: List[str]
    rectangles: List[Rectangle] | None = None
    triangles: List[Triangle] | None = None
    arrows: List[Arrow] | None = None
    images: List[Image] | None = None
    # PNG-content: {filename: base64png}
    png_payloads: Dict[str, str] | None = None

    def to_jsonable(self) -> Dict[str, Any]:
        def conv_list(xs):
            return [asdict(x) if hasattr(x, "__dict__") else x for x in (xs or [])] 
        return {
             "messagetype": self.messagetype.value,
             "numbers": self.numbers,
             "texts": self.texts,
             "rectangles": conv_list(self.rectangles),
             "triangles": conv_list(self.triangles),
             "arrows": conv_list(self.arrows),
             "images": conv_list(self.images),
             "png_payloads": self.png_payloads or {},
            }

# Helper om PNG-bestanden als base64 mee te sturen (websocket heeft geen HTTP caching-headers,
# we laten de frontend zelf een cache bijhouden op basis van filename).
def load_pngs_as_b64(assets_dir: Path, filenames: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for fn in filenames:
        p = (assets_dir / fn)
        data = p.read_bytes()
        out[fn] = base64.b64encode(data).decode("ascii")
    return out

__all__ = [
    "LineType", "MessageType",
    "Rectangle", "Triangle", "Arrow", "Image",
    "Message", "load_pngs_as_b64",
]
# Einde backend/protocol.py