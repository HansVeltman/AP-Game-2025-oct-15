from pathlib import Path
from handlers import register
from dataclasses import replace
from protocol import Message, MessageType, Image, load_pngs_as_b64


# Canvas size used by the frontend canvas
CANVAS_W = 1400
CANVAS_H = 725

# Protocol types
from protocol import (
    Message, MessageType,
    Rectangle as PRectangle,
    Triangle as PTriangle,
    Arrow as PArrow,
    Image as PImage,
    LineType as PLineType,
    load_pngs_as_b64,
)

# Model data (coordinates are normalized 0..1)
from ModelData_RectangelsLinesAndTriangles import (
    RECTANGLES as MRECTS,
    TRIANGLES as MTRIS,
    LINES as MLINES,
    IMAGES as MIMAGES,
)

def _to_proto_linetype(lt) -> PLineType:
    if lt is None:
        return PLineType.SOLID
    name = str(lt).lower()
    if name == "solid":
        return PLineType.SOLID
    if name == "dashed":
        return PLineType.DASHED
    # "double" or unknown -> best-fit dotted
    return PLineType.DOTTED

def _sx(x: float) -> float:
    return float(x) * CANVAS_W

def _sy(y: float) -> float:
    return float(y) * CANVAS_H

def _rect(mr) -> PRectangle:
    return PRectangle(
        name=mr.name, text=mr.text, font=mr.font, fontsize=mr.fontsize, textcolor=mr.textcolor,
        x=_sx(mr.x), y=_sy(mr.y), w=_sx(mr.w), h=_sy(mr.h),
        linewidth=mr.linewidth, fill=mr.fill, stroke=mr.stroke,
        linetype=_to_proto_linetype(getattr(mr, "linetype", None)),
    )

def _tri(mt) -> PTriangle:
    # Model Triangle uses x,y,w,h; protocol expects the same fields (in pixels)
    return PTriangle(
        name=mt.name, text=mt.text, font=mt.font, fontsize=mt.fontsize, textcolor=mt.textcolor,
        x=_sx(mt.x), y=_sy(mt.y), w=_sx(mt.w), h=_sy(mt.h),
        linewidth=mt.linewidth, fill=mt.fill, stroke=mt.stroke,
        linetype=_to_proto_linetype(getattr(mt, "linetype", None)),
    )

def _arrow(ml) -> PArrow:
    # Lines are defined with endpoints; convert normalized -> pixels
    return PArrow(
        name=ml.name, text=ml.text, font=ml.font, fontsize=ml.fontsize, textcolor=ml.textcolor,
        x1=_sx(ml.x1), y1=_sy(ml.y1), x2=_sx(ml.x2), y2=_sy(ml.y2),
        linewidth=ml.linewidth, stroke=ml.stroke,
        linetype=_to_proto_linetype(getattr(ml, "linetype", None)),
        arrow=getattr(ml, "arrow", 12),
    )

def _img(mi) -> PImage:
    return PImage(
        name=mi.name, text=mi.text, font=mi.font, fontsize=mi.fontsize, textcolor=mi.textcolor,
        x=_sx(mi.x), y=_sy(mi.y), w=_sx(mi.w), h=_sy(mi.h), filename=mi.filename
    )

@register(MessageType.SHOWORGANIZATION)
async def handle_SHOWPROCESS(ws, *, numbers, texts, assets_dir: Path) -> Message:
    # Convert & scale model -> protocol (pixels)
    rects = [_rect(r) for r in MRECTS]
    tris  = [_tri(t) for t in MTRIS]
    arrs  = [_arrow(l) for l in MLINES]
    imgs  = [_img(i) for i in MIMAGES]

 #   rects = [replace(r, fill="#DF1616") if r.name == "Background" else r for r in rects]  # Replace because "Frozen" class

    # Pack PNG payloads so frontend can render without extra fetches
    pngs = [i.filename for i in MIMAGES if getattr(i, "filename", None)]
    png_payloads = load_pngs_as_b64(assets_dir, pngs) if pngs else {}

    msg = Message(
        messagetype=MessageType.SHOWORGANIZATION,
        numbers=numbers,
        texts=texts,
        rectangles=rects,
        triangles=tris,
        arrows=arrs,
        images=imgs,
        png_payloads=png_payloads,
        )
    resp = msg.to_jsonable()


    # 3) tweak ‘m vrijelijk (dit is nu een gewone dict/list-structuur)
    for r in resp.get("rectangles", []):
        if r.get("name") == "Background":
            r["fill"] = "#D2301F"

    for r in resp.get("images", []):
        if r.get("name") == "Counter":
            r["y"] = _sy(0.62)

    # voeg verantwoordelijkheidsblokken toe
    # Extra afbeeldingen toevoegen aan de bestaande payload
    extra_files = ["Purchase Responsible.png", "Production Responsible.png", "Finance Responsible.png",
                   "Distribution Responsible.png", "SalesAndMarketing Responsible.png"]  

    # 1) Zorg dat de PNG-bytes meegestuurd worden
    resp["png_payloads"].update(load_pngs_as_b64(assets_dir, extra_files))

    # 2) Voeg image-items toe (pixel-coördinaten). Gebruik _sx/_sy voor schaal 0..1 → px.
    resp.setdefault("images", []).extend([
        {
            "name": "Purchase Responsible", "text": "", "font": "Arial", "fontsize": 14, "textcolor": "#000",
            "x": _sx(0.0082), "y": _sy(0.82), "w": _sx(0.1244), "h": _sy(0.092),
            "filename": "Purchase Responsible.png",
        },
        {
            "name": "Production Responsible", "text": "", "font": "Arial", "fontsize": 14, "textcolor": "#000",
            "x": _sx(0.1607), "y": _sy(0.82), "w": _sx(0.1244), "h": _sy(0.092),
            "filename": "Production Responsible.png",
        },
        {
            "name": "Finance Responsible", "text": "", "font": "Arial", "fontsize": 14, "textcolor": "#000",
            "x": _sx(0.3532), "y": _sy(0.82), "w": _sx(0.1244), "h": _sy(0.092),
            "filename": "Finance Responsible.png",
        },
        {
            "name": "Distribution Responsible", "text": "", "font": "Arial", "fontsize": 14, "textcolor": "#000",
            "x": _sx(0.5457), "y": _sy(0.82), "w": _sx(0.1244), "h": _sy(0.092),
            "filename": "Distribution Responsible.png",
        },
        {
            "name": "SalesAndMarketing Responsible", "text": "", "font": "Arial", "fontsize": 14, "textcolor": "#000",
            "x": _sx(0.7186), "y": _sy(0.82), "w": _sx(0.1244), "h": _sy(0.092),
            "filename": "SalesAndMarketing Responsible.png",
        },
        ])


    # 4) geef de dict terug (backend stuurt ‘m zoals is)
    return resp
