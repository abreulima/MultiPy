import asyncio
import pickle 

ADDR = '127.0.0.1'
PORT = 8888

async def handle_client(reader, writer):
    
    while True:

        data = await reader.read(1024)

        if not data:
            break

        message = pickle.loads(data)
        print(f"Received {message}")

        writer.write(data)
        await writer.drain()

    print("Client disconnected")
    writer.close()


async def main():

    server = await asyncio.start_server(handle_client, ADDR, PORT)

    addr = server.sockets[0].getsockname()
    print(f"Server: {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
