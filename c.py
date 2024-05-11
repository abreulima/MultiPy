import asyncio
import glob
import pickle
import pygame
import sys
import os
import json
import io

TITLE = "MultPy"
WIDTH = 960
HEIGHT = 640

ADDRESS = "77.54.219.90"
PORT = 25565

BUFFERSIZE = 1024 * 2

SPRITES_FOLDER = "sprites/"

playerid = 0

sprites = []

map = 0

image_surface = None

png_files = glob.glob(os.path.join(SPRITES_FOLDER, "*.png"))

png_surfaces = [pygame.image.load(file) for file in png_files]

for file in png_files:
    cut_rect = pygame.Rect(0, 0, 32, 32)

    sprite = pygame.image.load(file)
    sprite = sprite.subsurface(cut_rect)
    sprite = pygame.transform.scale(sprite, (sprite.get_width() * 2, sprite.get_height() * 2))
    sprites.append(sprite)

"""
class Tilemap:
    def __init__(self):
        self.tile_size = 32
        self.level_data = self.load_level('map.json')
        self.tile_images = self.load_tile_images()

    def load_level(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)
        
    def load_tile_images(self):
        # Load tile images (replace these paths with your own images)
        tile_images = {
            1: pygame.image.load('TX Tileset Grass.png').convert(),  # Example: tile with ID 1
            # Add more tiles as needed
        }
        return tile_images
    
    def render(self):
        for layer in self.level_data['layerInstances']:
            if layer['__identifier'] == 'AutoLayer':
                for y, row in enumerate(layer['grid']):
                    for x, tile_id in enumerate(row):
                        if tile_id in self.tile_images:
                            self.screen.blit(self.tile_images[tile_id], (x * self.tile_size, y * self.tile_size))
"""

class Game:
     
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(TITLE)

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
        self.game.screen.blit(sprites[self.sprite_id], (self.x, self.y))

game = Game()
#tile_map = Tilemap()
client_player = Player(game=game, id=1, sprite_id=0, x=50, y=50)

players = []

async def send_message(reader, writer, message):
    writer.write(pickle.dumps(message))
    await writer.drain()


async def receive_message(reader):
    data = await reader.read(BUFFERSIZE)
    return pickle.loads(data)


async def main():
    # Connect to the server
    
    global image_surface

    reader, writer = await asyncio.open_connection(ADDRESS, PORT)

    await send_message(reader, writer, "Hello, server!")

    game_event_response = await receive_message(reader)

    if game_event_response[0] == "id_update":
        client_player.id = game_event_response[1]
        print("Player ID:", client_player.id)


    while True:


        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                await send_message(reader, writer, ["disconnect", client_player.id])
                pygame.quit()
                sys.exit()


            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    client_player.sprite_id = (client_player.sprite_id + 1) % len(sprites)
                    ##await send_message(reader, writer, ["sprite_update", client_player.sprite_id])

                if event.key == pygame.K_e:
                    client_player.sprite_id = (client_player.sprite_id - 1) % len(sprites)
                    ##await send_message(reader, writer, ["sprite_update", client_player.sprite_id])

                if event.key == pygame.K_LEFT:
                    client_player.vx = -10

                if event.key == pygame.K_RIGHT:
                    client_player.vx = 10

                if event.key == pygame.K_UP:
                    client_player.vy = -10

                if event.key == pygame.K_DOWN:
                    client_player.vy = 10 

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_LEFT:
                    client_player.vx = 0    

                if event.key == pygame.K_RIGHT:
                    client_player.vx = 0

                if event.key == pygame.K_UP:
                    client_player.vy = 0   

                if event.key == pygame.K_DOWN:
                    client_player.vy = 0   

        client_player.update()

        game.screen.fill((255, 255, 255))
        game.clock.tick(60)


        # Send player position to server
        await send_message(reader, writer, [
            "position_update",
            client_player.id,
            client_player.sprite_id,
            client_player.x,
            client_player.y
        ])

                # Receive player positions from server
        game_event_response = await receive_message(reader)

        if game_event_response[0] == "player_locations":
            players = [
                Player(game=game, id=player[0], sprite_id=player[1], x=player[2], y=player[3])
                for player in game_event_response[1:]
            ]

        if game_event_response[0] == "player_map":
            #pass
            #print("map incoming...")
            png_data = game_event_response[1]
            print(png_data)
            image_surface = pygame.image.load(io.BytesIO(png_data))
            #image_surface = pygame.image.fromstring(game_event_response[1], (14, 16), 'RGB')  # Adjust size as needed

        if image_surface != None:
            original_width, original_height = image_surface.get_size()
            new_width, new_height = original_width * 2, original_height * 2
            resized_image = pygame.transform.scale(image_surface, (new_width, new_height))
            #game.screen.blit(image_surface, (0, 0))


        for player in players:
            player.render()

        ##client_player.render()


        #tile_map.render()
        pygame.display.flip()



    writer.close()
    await writer.wait_closed()

# Run the main coroutine
asyncio.run(main())
        