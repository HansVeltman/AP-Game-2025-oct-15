# backend/smoketest.py
import asyncio, json
from backend import backend

async def main():
    # simulate ws=None; just call the function
    msg = {"messagetype": "SHOWSTART", "numbers": [], "texts": ["Start"]}
    reply = await backend.handle_text_message(json.dumps(msg))
    print("SHOWSTART ->", reply[:200], "...")
    # run simulation 1 day
    msg = {"messagetype": "RUNSIMULATION", "numbers": [1], "texts": ["Run"]}
    reply = await backend.handle_text_message(json.dumps(msg))
    print("RUNSIMULATION ->", reply[:200], "...")

if __name__ == "__main__":
    asyncio.run(main())
