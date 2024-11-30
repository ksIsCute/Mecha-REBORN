from revolt.ext import commands
import random

class Fun(commands.Cog):
    """Fun commands for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a dice with a given number of sides."""
        result = random.randint(1, sides)
        await ctx.send(f"You rolled a {result}!")

# this SHOULD in theory work
# TODO: make this not shit because it is
def setup(bot):
    bot.add_cog(Fun(bot))