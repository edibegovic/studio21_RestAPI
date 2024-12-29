import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import websockets
from uvicorn import Config, Server
import time
from datetime import datetime

current_song_state = {"stationId": "00001", "timestamp": None, "title": None}  # Static

state_lock = asyncio.Lock()
app = FastAPI()


def log_to_file(response):
    file_name = "studio21_history.txt"
    with open(file_name, "a") as file:  # Open the file in append mode
        file.write(
            json.dumps(response) + "\n"
        )  # Convert the response to JSON string and add a newline


async def websocket_listener(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "ping"}))
                    continue

                # Process "songChanged" events
                if data.get("type") == "songChanged":
                    # Get the last item from the studio21 array
                    song_data = data["data"].get("studio21").get("current", [])
                    if song_data:
                        title = song_data.get("title")
                        artist = song_data.get("artist")
                        print(f"Title: {title}, Artist: {artist}")
                        if title and artist:
                            async with state_lock:
                                current_song_state["title"] = f"{artist} - {title}"
                                current_song_state["timestamp"] = (
                                    datetime.fromtimestamp(time.time()).strftime(
                                        "%d-%m-%Y %H:%M"
                                    )
                                )
                                log_to_file(current_song_state)
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)


@app.get("/current_song")
async def get_current_song():
    async with state_lock:
        return JSONResponse(content=current_song_state)


async def start_uvicorn():
    config = Config(app=app, host="0.0.0.0", port=8000)
    server = Server(config)
    await server.serve()


async def main():
    uri = "wss://node.studio21.ru/"
    await asyncio.gather(
        websocket_listener(uri),
        start_uvicorn(),
    )


if __name__ == "__main__":
    asyncio.run(main())


import pipreqs

pipreqs
