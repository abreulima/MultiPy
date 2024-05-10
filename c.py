import asyncio
import pickle
import pygame
import sys

TITLE = "MultPy"
WIDTH = 800
HEIGHT = 600

ADDRESS = "127.0.0.1"
PORT = 4333

BUFFERSIZE = 2048

playerid = 0

sprite1 = pygame.image.load('sprites/Imagem-1.png')


class Game:
     
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(TITLE)

class GameEvent:

    def __init__(self, vx, vy):
        self.vx = vx
        self.vy = vy

class Player(pygame.sprite.Sprite):
    def __init__(self, game, id, sprite_id, x, y):
        super().__init__()

        self.game = game
        self.id = id
        self.sprite_id = sprite_id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0


    def update(self):

        self.x += self.vx
        self.y += self.vy

        if self.id == 0:
            self.id = playerid
    
    def render(self):
        self.game.screen.blit(sprite1, (self.x, self.y))

game = Game()
client_player = Player(game=game, id=1, sprite_id=50, x=50, y=50)

players = []

async def send_message(message):
    # Connect to the server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    game_event = await reader.read(1024)
    game_event_response = pickle.loads(game_event)
    print(f"Received response from server: {game_event_response}")

    if game_event_response[0] == "id_update":
        client_player.id = game_event_response[1]
        print("Player ID", client_player.id)



    while True:

        #user_input = input("Enter Movement")
        ##serialized_message = pickle.dumps("a")
        ##writer.write(serialized_message)
        ##await writer.drain()

        
        # Read the response from the server
        #response = await reader.read(1024)
        #response_message = pickle.loads(response)
        #print(f"Received response from server: {response_message}")
        
        #done, pending = await asyncio.wait([reader], timeout=0)

        #for task in done:
        #    data = await task.result().read(1024)
        #    print(pickle.loads(data))

        #if game_event[0] == "id_update":
        #    pass
            #Player.playerid = game_event[1]
            #print(playerid)


        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


            if event.type == pygame.KEYDOWN:
            
                if event.key == pygame.K_LEFT:
                    client_player.vx = -10

                if event.key == pygame.K_RIGHT:
                    client_player.vx = 10

                if event.key == pygame.K_UP:
                    client_player.vy = -10

                if event.key == pygame.K_DOWN:
                    client_player.vy = 10 

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_LEFT and client_player.vx == -10:
                    client_player.vx = 0    

                if event.key == pygame.K_RIGHT and client_player.vx == 10:
                    client_player.vx = 0

                if event.key == pygame.K_UP and client_player.vy == -10:
                    client_player.vy = 0   

                if event.key == pygame.K_DOWN and client_player.vy == 10:
                    client_player.vy = 0   


        game.clock.tick(60)
        game.screen.fill((255, 255, 255))

        client_player.update()

        for player in players:
            player.render()

        client_player.render()

        pygame.display.flip()


        updateLocation = [
            "position_update",
            client_player.id,
            client_player.x,
            client_player.y
        ]


        writer.write(pickle.dumps(updateLocation))
        await writer.drain()


    writer.close()
    await writer.wait_closed()

async def main():
    # Send a message to the server
    await send_message("Hello, server!")

# Run the main coroutine
asyncio.run(main())
        