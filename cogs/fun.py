from revolt.ext import commands
from main import Client
import random

class Fun(commands.Cog):
    """Fun commands for the bot."""

    def __init__(self, bot: Client):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, sides):
        """Roll a dice with a given number of sides."""
        if isinstance(sides, int):
            sides = int(sides)
        else: 
            sides = 6
        result = random.randint(1, sides)
        await ctx.send(f"You rolled a {result}!")

# this SHOULD in theory work
# TODO: make this not shit because it is
def setup(bot):
    bot.add_cog(Fun(bot))