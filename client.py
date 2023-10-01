import asyncio
import websockets

async def send_data():
    uri = "ws://localhost:1234"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                data = input("Enter data to send: ")
                await websocket.send(data)
                
                response = await websocket.recv()
                print(f"Received response: {response}")
            except websockets.exceptions.ConnectionClosedError:
                break

asyncio.get_event_loop().run_until_complete(send_data())