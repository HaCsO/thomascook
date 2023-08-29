import discord
from discord.ext import commands
from .__utils import WatchingAct

hail_channel = 704078802032263188
rules_channel = 864929428093927464
dolboebi = "https://cdn.discordapp.com/attachments/1073367249542447154/1146058241206403163/video_2023-07-22_10-23-19.mp4"

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot    

    @commands.Cog.listener()
    async def on_ready(self):
        act = WatchingAct()
        await self.bot.change_presence(activity=act)
        print("Bot ready")
 
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        await self.bot.get_channel(hail_channel).send(
            f"Привет {member.mention}, добро пожаловать на Discord-сервер **Thomas Cook Airlines**! Не забудь заглянуть в канал <#{rules_channel}> чтобы получить доступ ко всем функциям"
        )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if self.bot.user.mention in msg.content:
            await msg.reply(dolboebi)

def setup(bot):
    bot.add_cog(Events(bot))
    print("Events loaded!")