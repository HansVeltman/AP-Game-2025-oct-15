from __future__ import annotations
from typing import Callable, Awaitable, Dict
from pathlib import Path


from protocol import MessageType, Message


Handler = Callable[..., Awaitable[Message]]
registry: Dict[MessageType, Handler] = {}


def register(mtype: MessageType):
    def deco(fn: Handler) -> Handler:
        registry[mtype] = fn
        return fn
    return deco


# import side-effect: registreert alle handlers
from . import handle_SHOWSTART, handle_SHOWSTRATEGY, handle_SHOWPROCESS, \
handle_SHOWCONTROL, handle_SHOWORGANIZATION, handle_SHOWINFORMATION, \
handle_RUNSIMULATION # noqa: F401