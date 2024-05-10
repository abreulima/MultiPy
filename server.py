import asyncio
import random
import pickle
import socket

PORT = 4333

BUFFERSIZE = 2048

outgoing = []
playersmap = {}

class Player:
    def __init__(self, ownerid):
        self.x = 0
        self.y = 0
        self.sprite_id = 0
        self.ownerid = ownerid

async def updateWorld(message):
    global outgoing
    global playersmap

    arr = pickle.loads(message)
    print(arr[0])

    playerid = arr[1]
    x = arr[2]
    y = arr[3]
    sprite_id = arr[4]

    if playerid == 0:
        return
    
    playersmap[playerid].x = x
    playersmap[playerid].y = y
    playersmap[playerid].sprite_id = sprite_id


    update = ["player locations"]

    for key, value in playersmap.items():
        update.append([value.ownerid, value.x, value.y, value.sprite_id])

    remove = []

    for i in outgoing:
        try:
            i.write(pickle.dumps(update))
            await i.drain()
        except Exception:
            remove.append(i)

    for r in remove:
        outgoing.remove(r)


async def handle_client(reader, writer):
    global outgoing
    global playersmap

    playerID = random.randint(0, 100000)
    mainplayer = Player(playerID)
    playersmap[playerID] = mainplayer

    writer.write(pickle.dumps(["id update", playerID]))
    await writer.drain()

    outgoing.append(writer)

    while True:
        data = await reader.read(BUFFERSIZE)
        
        if not data:
            break
        await updateWorld(data)

async def main():
    server = await asyncio.start_server(handle_client, '', PORT)
    async with server:
        await server.serve_forever()

asyncio.run(main())

