import asyncore
import asyncio
import random
import pickle
import socket

BUFFERSIZE = 2048

outgoing = []
playersmap = {}

class Player:
    def __init__(self, ownerid):
        self.x = 0
        self.y = 0
        self.sprite_id = 0
        self.ownerid = ownerid

def updateWorld(message):
    arr = pickle.loads(message)
    print(str(arr))
    playerid = arr[1]
    x = arr[2]
    y = arr[3]
    sprite_id = arr[4]

    if playerid == 0:
        return
    
    playersmap[playerid].x = x
    playersmap[playerid].y = y
    playersmap[playerid].sprite_id = sprite_id

    remove = []

    for i in outgoing:

        update = ["player locations"]

        for key, value in playersmap.items():
            update.append([value.ownerid, value.x, value.y, value.sprite_id])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        print("sent update data")

        for r in remove:
            outgoing.remove(r)


class MainServer(asyncore.dispatcher):
    
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()

        outgoing.append(conn)
        playerID = random.randint(0, 100000)
        mainplayer = Player(playerID)
        playersmap[playerID] = mainplayer

        conn.send(pickle.dumps(["id update", playerID]))

        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):

    def handle_read(self):
        receivedData = self.recv(BUFFERSIZE)

        if receivedData:
            updateWorld(receivedData)
        else:
            self.close()



MainServer(4321)
asyncore.loop()


