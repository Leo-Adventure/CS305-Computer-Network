import asyncio
import time
from socket import create_connection
from xml.etree.ElementTree import tostring

import websockets

clients = []
connected = []
JOIN = {}
history = []


class DanmakuServer:
    """
    Receive danmakus from clients, reply them correctly
    """
    
    def __init__(self):
        # TODO: define your variables needed in this class
        
        print("I'd like to run now")
        # raise NotImplementedError

    async def reply(self, websocket):
        # TODO: design your reply method
        # print("I cannot reply you: {}".format(websocket))
        ticks = int(time.time() % 10086)
        name = "user" + str(ticks)
        clients.append(name)
        # print("Now we have ")
        # print(clients)
        connected.append(websocket)
        for msg in history:
            await websocket.send(msg)

        try:
            while True: 
                msg = await websocket.recv() 
                history.append(msg)
                websockets.broadcast(connected, msg)
                # print ("Receive a message: {}".format(msg))

        except websockets.exceptions.ConnectionClosedOK:
            print("Bye{}".format(name))
        finally:
            clients.remove(name)
            connected.remove(websocket)
            websocket.close()
            print(len(connected))
            print("{} has been removed".format(name))
        # raise NotImplementedError


if __name__ == "__main__":
    server = DanmakuServer()
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(server.reply, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()
