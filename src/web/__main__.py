import asyncio
from src.web.server import GameServer

if __name__ == "__main__":
    server = GameServer()
    asyncio.run(server.start())
