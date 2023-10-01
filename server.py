import asyncio
import websockets

async def handle_client(websocket, path):
    while True:
        try:
            data = await websocket.recv()
            # Process received data
            print(f"Received data: {data}")
            
            # Send response back to the client
            response = "Server received data"
            await websocket.send(response)
        except websockets.exceptions.ConnectionClosedError:
            break

start_server = websockets.serve(handle_client, 'localhost', 1234)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()