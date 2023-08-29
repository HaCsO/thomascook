import discord
from discord.ext import commands
import configparser
import os
bot = commands.Bot(command_prefix="!", intents= discord.Intents.default(), debug_guilds=[686268385138573487])

cogs = [
	"cogs.events",
	# "cogs.cloud",
	"cogs.stats"
]
for i in cogs:
	bot.load_extension(i)
cfg = configparser.ConfigParser()
cfg.read("./config.cfg")
bot.run(cfg["GENERAL"]["token"])