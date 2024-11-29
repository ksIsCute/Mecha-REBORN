import asyncio

import aiohttp

import revolt, json
from revolt.ext import commands

with open("/config/config.json") as f:
    config = json.load(f)

class Client(commands.CommandsClient):
    async def get_prefix(self, message: revolt.Message):
        return commands.when_mentioned_or(config['PREFIX'])(self, message)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("pong")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config['TOKEN'])
        await client.start()

asyncio.run(main())