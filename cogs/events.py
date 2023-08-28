import discord
from discord.ext import commands

hail_channel = 704078802032263188
rules_channel = 864929428093927464

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # await self.bot.change_presence(activity=discord.CustomActivity(name= "Смотрит прямо в душу"))
        print("Bot ready")
 
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        await self.bot.get_channel(hail_channel).send(
            f"Привет {member.mention}, добро пожаловать на Discord-сервер **Thomas Cook Airlines**! Не забудь заглянуть в канал <#{rules_channel}> чтобы получить доступ ко всем функциям"
        )

def setup(bot):
    bot.add_cog(Events(bot))
    print("Events loaded!")