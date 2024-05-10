import asyncio
import pickle
import pygame


TITLE = "MultPy"
WIDTH = 800
HEIGHT = 600

ADDRESS = "127.0.0.1"
PORT = 4333

BUFFERSIZE = 2048

class Game:
     
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(TITLE)

class Player(pygame.sprite.Sprite):
     pass


async def send_message(message):
    # Connect to the server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        while True:

            user_input = input("Enter Movement")
            serialized_message = pickle.dumps(user_input)

            writer.write(serialized_message)
            await writer.drain()

            """
            # Read the response from the server
            response = await reader.read(1024)
            response_message = pickle.loads(response)
            print(f"Received response from server: {response_message}")
            """

    except KeyboardInterrupt:
            pass

    finally:
        # Close the connection
        writer.close()
        await writer.wait_closed()

async def main():
    # Send a message to the server
    await send_message("Hello, server!")

# Run the main coroutine
asyncio.run(main())
        