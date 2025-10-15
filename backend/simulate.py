# backend/simulate.py
from __future__ import annotations


# Global simulation day counter
SimDayNumber: int = 0

def SimulategameOneDay() -> int:

    # do all the compex simulation stuff here
    global SimDayNumber
    SimDayNumber += 1
    return SimDayNumber


def ResetSimulation() -> int:
   
   # do all the cleanup work here
   
    global SimDayNumber
    SimDayNumber =0;
    return SimDayNumber