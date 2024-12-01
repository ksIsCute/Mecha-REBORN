from revolt.ext import commands
from main import Client
import random

class Test(commands.Cog):
    """Test commands for the bot."""

    def __init__(self, bot: Client):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx, sides: int = 6):
        await ctx.send(random.randint(1, sides))

def setup(bot):
    bot.add_cog(Test(bot))