import revolt, json
from revolt.ext import commands

from main import Client

with open("config/config.json") as f:
    config = json.load(f)

class Auto(commands.Cog):
    def __init__(self, bot: revolt.Client):
        self.bot = bot

    @commands.command()
    async def aut(self, ctx: revolt.Context):
        """Ping the bot."""
        await ctx.send("Pong!")


def setup(client: Client):
    client.add_cog(Auto())