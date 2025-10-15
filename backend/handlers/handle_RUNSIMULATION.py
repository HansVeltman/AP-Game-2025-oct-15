from __future__ import annotations
from pathlib import Path
from handlers import register
from protocol import Message, MessageType
from datetime import date, timedelta
import calendar
import simulate


@register(MessageType.RUNSIMULATION)
async def handle_RUNSIMULATION(ws, *, numbers, texts, assets_dir: Path) -> Message:
    # 1) Lees gewenste aantal dagen uit de payload
    #    (numbers kan leeg of None zijn → default 1 dag)
    try:
        days_to_simulate = int(numbers[0]) if numbers and len(numbers) > 0 else 1
    except Exception:
        days_to_simulate = 1

    # 2) Speciaal geval: "30" betekent "simuleer één kalendermaand"
    #    We bepalen dan het aantal dagen van de huidige kalendermaand gemeten
    #    vanaf de simulatiedatum (vandaag + SimDayNumber).
    if days_to_simulate == 30:
        start_date = date.today() + timedelta(days=simulate.SimDayNumber)
        _, month_len = calendar.monthrange(start_date.year, start_date.month)  # 28/29/30/31
        days_to_simulate = month_len

    # 3) Voer de simulatie uit
    for _ in range(max(0, days_to_simulate)):
        simulate.SimulategameOneDay()

    if days_to_simulate == -1:        
        simulate.ResetSimulation()
        

    # 4) Antwoord terug naar de frontend
    return Message(
        messagetype=MessageType.RUNSIMULATION,
        numbers=[simulate.SimDayNumber],     # actuele totale SimDayNumber
        texts=["Runned one day"],            # laat zo als je frontend daarop rekent
        rectangles=[], triangles=[], arrows=[], images=[],
        png_payloads={},
    )
    # Opmerking: de frontend berekent zelf de datum op basis van SimDayNumber

