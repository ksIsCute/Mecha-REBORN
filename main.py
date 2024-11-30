import asyncio
import random
import psutil
import os
import time
import aiohttp
from funny import ping_responses

import revolt, json
from revolt.ext import commands

# TODO: Setup mongoDB and motor (async mongo.py) (ks will do this)
# TODO: Setup cogs for organization of ideas (miku will do this :D ) 
# TODO: setup logging & other utilities
# TODO: setup command cooldowns
# TODO: brainstorm commands
# TODO: economy commands
# TODO: setup database (we will be resetting it) (ks will do this)
# TODO: logo stuff & pr related shit
# TODO: setup support server / system
# TODO: exclusive ticket system for support server
# TODO: custom emoji assets
# TODO: custom status
# TODO: custom command prefix

with open("config/config.json") as f:
    config = json.load(f)

    
class Client(commands.CommandsClient):
    def __init__(self, session: aiohttp.ClientSession, token: str):
        self.uptime = time.time()
        super().__init__(session, token)
               
    async def get_prefix(self, message: revolt.Message):
        return config['PREFIX'] # FIXME: make this custom later

    async def on_message(self, message: revolt.Message):
        await self.process_commands(message)

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
                    "{server.member_count}": str(len(member.server.members)),
                    "{server.channel_count}": str(len(member.server.channels)),
                    "{server.role_count}": str(len(member.server.roles)),
                    "{server.emoji_count}": str(len(member.server.emojis)),
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
    async def stats(self, ctx: commands.Context):
        member_count = 0
        servers = []
        for server in self.servers:
            member_count += len(server.members)
            servers.append((server.name, len(server.members)))
        servers.sort(key=lambda x: x[1], reverse=True)
        sep = "\n"
        embed = revolt.SendableEmbed(
            title="Member Count",
            description=f"**Uptime**\n`{', '.join([f'{int(value)}{unit}' for unit, value in [('d', (time.time() - self.uptime) // 86400), ('h', ((time.time() - self.uptime) % 86400) // 3600), ('m', ((time.time() - self.uptime) % 3600) // 60), ('s', (time.time() - self.uptime) % 60)] if value != 0])}`\n**Total member count:**\n`{member_count}`\n**Top 3 biggest contributors:**\n{sep.join([f'*{server[0]}* - `{server[1]}`' for server in servers[:3]])}",
            colour = "#00ff00"
        )
        await ctx.send(embeds=[embed])

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config['TOKEN'])
        await client.start()

asyncio.run(main())