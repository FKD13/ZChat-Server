import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

event: asyncio.Event = asyncio.Event()
message: str = ""


def do(f):
    async def wrapper(*args, **kwargs):
        try:
            while True:
                await f(*args, **kwargs)
        except WebSocketDisconnect:
            pass

    return wrapper


@do
async def receive_messages(websocket: WebSocket):
    global message
    _message = await websocket.receive_text()
    if 0 < len(_message) <= 64:
        message = _message
        event.set()
    event.clear()
    await asyncio.sleep(0.1)


@do
async def send_messages(websocket: WebSocket):
    await event.wait()
    await websocket.send_text(message)


@app.websocket("/chat")
async def send(websocket: WebSocket):
    await websocket.accept()
    await asyncio.gather(receive_messages(websocket), send_messages(websocket))
