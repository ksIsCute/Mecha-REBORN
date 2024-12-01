import revolt, json
from revolt.ext import commands

from main import Client

with open("config/config.json") as f:
    config = json.load(f)

class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def aut(self, ctx):
        """Ping the bot."""
        await ctx.send("Pong!")


def setup(bot):
    bot.add_cog(Auto(bot))