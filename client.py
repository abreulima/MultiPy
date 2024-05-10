import pygame, sys
from pygame.locals import *

import glob
import pickle
import select
import asyncio

TITLE = "MultPy"
WIDTH = 800
HEIGHT = 600

ADDRESS = "127.0.0.1"
PORT = 4333

BUFFERSIZE = 2048

sprites_folder = "sprites/"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

##sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##sckt.connect((ADDRESS, PORT))

sprites = []

png_files = glob.glob(sprites_folder + "*.png")

png_surfaces = [pygame.image.load(file) for file in png_files]


for file in png_files:
    cut_rect = pygame.Rect(0, 0, 32, 32)

    sprite = pygame.image.load(file)
    sprite = sprite.subsurface(cut_rect)
    sprite = pygame.transform.scale(sprite, (sprite.get_width() * 2, sprite.get_height() * 2))

    sprites.append(sprite)

playerId = 0

class Player:

    def __init__(self, x, y, id, sprite_id):
        self.id = id
        self.sprite_id = sprite_id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy


        """
        if self.x > WIDTH - 32:
            self.x = WIDTH - 32
        if self.x < 0:
            self.x = 0
        if self.y > HEIGHT - 32:
            self.y = HEIGHT - 32
        if self.y < 0:
            self.y = 0
        """

        if self.id == 0:
            self.id = playerId

    def render(self, camera_x, camera_y):
        #screen.blit(sprites[self.sprite_id], (self.x, self.y))
        screen.blit(sprites[self.sprite_id], (self.x - camera_x, self.y - camera_y))

class GameEvent:

    def __init__(self, vx, ty):
        self.vx = vx
        self.vy = vx

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        #self.display_surface = pygame.display.get_surface()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self):
        for sprite in self.sprites():
            screen.blit(sprite.image, sprite.rect)

camera_group = CameraGroup()

clientPlayer = Player(50, 50, 0, 0)

players = []

async def handle_data(reader, writer):
    global playerId
    global clientPlayer
    global players

    while True:
        data = await reader.read(BUFFERSIZE)
        if not data:
            break
        gameEvent = pickle.loads(data)
        print(gameEvent)

        if gameEvent[0] == "id update":
            playerId = gameEvent[1]
            print(playerId)

        if gameEvent[0] == "player locations":
            gameEvent.pop(0)

            players = []

            for player in gameEvent:
                if player[0] != playerId:
                    players.append(
                        Player(player[1], player[2], player[0], player[3])
                    )
async def main():
    global playerId
    global clientPlayer
    global players

    reader, writer = await asyncio.open_connection(ADDRESS, PORT)

    clientPlayer = Player(50, 50, 0, 0)
    players = []

    writer.write(pickle.dumps(["id update", playerId]))
    await writer.drain()

    while True:
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_LEFT: clientPlayer.vx = -10
                if event.key == K_RIGHT: clientPlayer.vx = 10
                if event.key == K_UP: clientPlayer.vy = -10
                if event.key == K_DOWN: clientPlayer.vy = 10
                
                if event.key == K_r: 
                    clientPlayer.sprite_id += 1

            if event.type == KEYUP:
                if event.key == K_LEFT and clientPlayer.vx == -10: clientPlayer.vx = 0
                if event.key == K_RIGHT and clientPlayer.vx == 10: clientPlayer.vx = 0
                if event.key == K_UP and clientPlayer.vy == -10: clientPlayer.vy = 0
                if event.key == K_DOWN and clientPlayer.vy == 10: clientPlayer.vy = 0

        clientPlayer.update()

        writer.write(pickle.dumps(["position update", playerId, clientPlayer.x, clientPlayer.y, clientPlayer.sprite_id]))
        await writer.drain()

        clock.tick(60)
        screen.fill((255, 255, 255))

        camera_x = max(0, min(clientPlayer.x - WIDTH // 2, WIDTH - WIDTH))
        camera_y = max(0, min(clientPlayer.y - HEIGHT // 2, HEIGHT - HEIGHT))

        for player in players:
            player.render(camera_x, camera_y)

        clientPlayer.render(camera_x, camera_y)

        pygame.display.flip()

asyncio.run(main())