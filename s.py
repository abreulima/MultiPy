import asyncio
import pickle
import random


ADDR = '0.0.0.0'
PORT = 25565

BUFFERSIZE = 1024 * 2

connections = []
player_map_file = None
players_map = {}

class Player:
    def __init__(self, owner_id, sprite_id):
        self.owner_id = owner_id
        self.sprite_id = sprite_id
        self.x = 0
        self.y = 0


async def handle_client(reader, writer):

    connections.append(writer)
    
    player_id = random.randint(0, 100000)
    main_player = Player(player_id, 0)
    players_map[player_id] = main_player

    writer.write(pickle.dumps(["id_update", player_id]))
    await writer.drain()


    while True:

        data = await reader.read(BUFFERSIZE)

        if not data:
            break

        message = pickle.loads(data)
        #print(f"Received {message}")
        

        if message[0] == "position_update":

            player_id = message[1]
            player_sprite_id = message[2]
            x = message[3]
            y = message[4]

            ##print(message[1], message[2], message[3], message[4])

            if player_id == 0:
                return
            
            players_map[player_id].x = x
            players_map[player_id].y = y
            players_map[player_id].sprite_id = player_sprite_id


        if message[0] == "map_update":
            print("Map incoming...")
            #print(message[1])
            player_map_file = message[1]


        remove = []
        
        for conn in connections:

            if message[0] == "position_update":

                update = ["player_locations"]

                for key, value in players_map.items():
                    update.append([value.owner_id, value.sprite_id, value.x, value.y])

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


            if message[0] == "map_update":

                update = ["player_map", player_map_file]

                print("to send", update)

                #for key, value in players_map.items():
                #    update.append(player_map_file)

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

    connections.remove(writer)

    for key, value in players_map.items():
        if value.owner_id == player_id:
            del players_map[key]
            break

    writer.close()


async def main():

    server = await asyncio.start_server(handle_client, ADDR, PORT)

    addr = server.sockets[0].getsockname()
    print(f"Server: {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
