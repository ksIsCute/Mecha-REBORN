from revolt.ext import commands 
from main import Client

class Hi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command
    async def hello(self,ctx):
        await ctx.send("hello!!! :D")
        
def setup(client: Client):
    client.add_cog(Hi())