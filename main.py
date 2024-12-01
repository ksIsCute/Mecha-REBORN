from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import datetime
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
        self.avatar_path = "assets/temp.png"  # Path to the bot's avatar
        super().__init__(session, token)

    def load_extensions(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    Client.load_extension(self, f"cogs.{filename[:-3]}")
                    print(f"Loaded {filename[:-3]} Cog!")
                except Exception as e:
                    print(e)

    async def get_prefix(self, message: revolt.Message):
        return config['PREFIX'] # FIXME: make this custom later

    async def on_message(self, message: revolt.Message):
        await self.process_commands(message)

    async def on_ready(self):
        print(f"Logged in")
        self.load_extensions()

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

        # Calculate progress for the next milestone
        milestone = ((member_count // 5000) + 1) * 5000  # Next milestone
        progress = member_count / milestone

        # Create image
        img_width, img_height = 800, 400
        image = Image.new("RGB", (img_width, img_height))
        draw = ImageDraw.Draw(image)

        # Create gradient background: Grey to Dark Grey
        for y in range(img_height):
            # Interpolate between grey (102) and dark grey (51) for each color channel
            r = int(102 + (51 - 102) * (y / img_height))  # Transition red
            g = int(102 + (51 - 102) * (y / img_height))  # Transition green
            b = int(102 + (51 - 102) * (y / img_height))  # Transition blue
            draw.line([(0, y), (img_width, y)], fill=(r, g, b))

        # Fonts
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_large = ImageFont.truetype(font_path, 36)
        font_medium = ImageFont.truetype(font_path, 28)
        font_small = ImageFont.truetype(font_path, 20)
        font_bold_large = ImageFont.truetype(font_path, 40)
        font_bold_medium = ImageFont.truetype(font_path, 30)

        # Add centered "Session  Statistics" label
        draw.text((img_width // 2, 20), "Session Statistics", fill="white", font=font_bold_large, anchor="mm")

        # Add bot avatar cropped as a circle
        avatar_size = 60
        avatar = Image.open(self.avatar_path).convert("RGBA")
        avatar = avatar.resize((avatar_size, avatar_size))
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        avatar = ImageOps.fit(avatar, (avatar_size, avatar_size), centering=(0.5, 0.5))
        avatar.putalpha(mask)

        # Position for avatar and text
        avatar_x, avatar_y = img_width - 160, 20
        text_x, text_y = img_width - 90, 25

        # Paste avatar onto the image
        image.paste(avatar, (avatar_x, avatar_y), mask=avatar)

        # Add "Mecha" text beside the avatar
        draw.text((text_x, text_y), "Mecha", fill="white", font=font_medium)

        # CPU usage (top right below "Mecha")
        cpu_usage = psutil.cpu_percent()
        draw.text((text_x, text_y + 35), f"{cpu_usage:.1f}%", fill="white", font=font_small)

        # Member count milestone progress bar
        bar_x, bar_y, bar_width, bar_height = 50, 150, 700, 30
        progress_width = int(bar_width * progress)

        # Background for progress bar
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(100, 100, 100))

        # Gradient fill for the progress bar
        for x in range(progress_width):
            r = int(173 + (90 - 173) * (x / progress_width))  # Blue to darker blue
            g = int(216 + (90 - 216) * (x / progress_width))
            b = int(230 + (90 - 230) * (x / progress_width))
            draw.line([(bar_x + x, bar_y), (bar_x + x, bar_y + bar_height)], fill=(r, g, b))

        # Add text for member count and milestone
        draw.text((bar_x, bar_y - 40), f"{member_count}", fill="white", font=font_small, anchor="lt")
        draw.text((bar_x + bar_width, bar_y - 40), f"{milestone}", fill="white", font=font_small, anchor="rt")

        # Top Servers Section
        draw.text((50, 200), "Top Servers:", fill="white", font=font_bold_medium)
        top_servers_text = "\n".join([f"{server[0]}: {server[1]}" for server in servers[:3]])
        draw.text((50, 240), top_servers_text, fill="white", font=font_medium)

        # Uptime (bottom right)
        uptime_seconds = time.time() - self.uptime
        uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))
        draw.text((img_width - 200, img_height - 40), f"Uptime: {uptime_string}", fill="white", font=font_small)

        # Save to a BytesIO buffer
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Extract bytes and send the image
        image_bytes = buffer.getvalue()
        file = revolt.File(image_bytes, filename="stats.png")
        await ctx.send(attachments=[file])


    @commands.command(aliases=['av', 'avatar'])
    async def avatar(self, ctx: commands.Context, member: revolt.Member=None):
        if member is None:
            member = ctx.author
            url = member.avatar.url
        if member.avatar is None:
            url = member.default_avatar.url
        else:
            url = member.avatar.url
        await ctx.send(url)

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config['TOKEN'])
        await client.start()

if __name__ == '__main__':
    asyncio.run(main())