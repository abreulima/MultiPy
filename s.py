import asyncio
import pickle
import random


ADDR = '127.0.0.1'
PORT = 8888

connections = []
players_map = {}

class Player:
    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.x = 0
        self.y = 0


async def handle_client(reader, writer):

    connections.append(writer)
    
    player_id = random.randint(0, 100000)
    main_player = Player(player_id)
    players_map[player_id] = main_player

    writer.write(pickle.dumps(["id_update", player_id]))
    await writer.drain()


    while True:

        data = await reader.read(1024)

        if not data:
            break

        message = pickle.loads(data)
        #print(f"Received {message}")
        

        if message[0] == "position_update":

            player_id = message[1]
            x = message[2]
            y = message[3]

            print(message[1], message[2], message[3])

            if player_id == 0:
                return
            
            players_map[player_id].x = x
            players_map[player_id].y = y


        remove = []
        
        for conn in connections:

            update = ["player_locations"]

            for key, value in players_map.items():
                update.append([value.owner_id, value.x, value.y])

            try:
                conn.write(pickle.dumps(update))
                await conn.drain()
            except asyncio.CancelledError:
                remove.append(conn)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                remove.append(conn)

            for r in remove:
                connections.remove(r)

    print("Client disconnected")
    writer.close()


async def main():

    server = await asyncio.start_server(handle_client, ADDR, PORT)

    addr = server.sockets[0].getsockname()
    print(f"Server: {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
