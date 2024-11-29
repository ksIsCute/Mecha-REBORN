import asyncio
import random
import psutil
import time
import aiohttp
from funny import ping_responses

import revolt, json
from revolt.ext import commands

with open("config/config.json") as f:
    config = json.load(f)

class Client(commands.CommandsClient):
    async def get_prefix(self, message: revolt.Message):
        return config['PREFIX']
    
    async def on_ready(self):
        print(f"Logged in")
    
    async def on_member_join(self, member: revolt.Member):
        if member.server.id in config['SERVERS']:
            if config['SERVERS'][member.server.id]['autorole']['enabled']:
                role = member.server.get_role(config['SERVERS'][member.server.id]['autorole']['role'])
                await member.edit(roles=[role])
            if config['SERVERS'][member.server.id]['welcome']['enabled']:
                channel = Client.get_channel(self, config['SERVERS'][member.server.id]['welcome']['channel'])
                variables = {
                    "{member.mention}": member.mention,
                    "{member.name}": member.name,
                    "{member.discriminator}": member.discriminator,
                    "{member.id}": str(member.id),
                    "{server.name}": member.server.name,
                    "{server.id}": str(member.server.id),
                }
                message = config['SERVERS'][member.server.id]['welcome']['message']
                embed = revolt.SendableEmbed()
                if message['embed']['enabled']:
                    embed.title = message['embed']['title']
                    embed.colour = message['embed']['color']
                    embed.description = message['embed']['description']
                    for key, value in variables.items():
                        embed.description = embed.description.replace(key, value)
                for key, value in variables.items():
                    message['content'] = message['content'].replace(key, value)
                await channel.send(message['content'], embeds=[embed])

    @commands.command()
    async def ping(self, ctx: commands.Context):
        start = time.time()
        msg = await ctx.send(f"Pinging **{random.choice(ping_responses)}**...")
        cpuusage = psutil.cpu_percent(5)
        embed = revolt.SendableEmbed(
            description=f"**{round((time.time() - start) * 1000) - 5000}ms**\n**CPU Usage:** `{cpuusage}%`",
        )
        await msg.edit(content=f"Pong!", embeds=[embed])

    @commands.command()
    async def empty(self, ctx: commands.Context):
        embed = revolt.SendableEmbed(
            colour="#00ff00"
        )
        await ctx.send(embeds=[embed])

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config['TOKEN'])
        await client.start()

asyncio.run(main())