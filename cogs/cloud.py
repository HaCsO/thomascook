import discord
from discord.ext import commands
from .__utils import is_approved_channel
import json
import os

sim_types = [
	discord.OptionChoice(name="xplane"),
	discord.OptionChoice(name="p3d"),
	discord.OptionChoice(name="mfs")
]

def autocomplete_sims(ctx):
	return sim_types

class CloudCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@is_approved_channel()
	@commands.slash_command()
	async def livery(self, ctx):
		await ctx.respond("https://vk.com/@thomascookairlines-livrei-thomas-cook")

	@is_approved_channel()
	@commands.slash_command()
	async def model(self, ctx, sim: discord.Option(name= "simulator", choises=sim_types, autocomplete= autocomplete_sims), plane: discord.Option(name="plane", input_type=str)):
		with open("/root/thomascook/links.json", "r") as f:
			data = json.load(f)
		try:
			await ctx.respond(f"Симулятор: {sim}\nМодель: {plane}\nСсылка: {data['model'][sim][plane]}")
		except:
			await ctx.respond("Что то пошло не так... Такой самолет небыл найден!")

	@is_approved_channel()
	@commands.slash_command()
	async def scenery(self, ctx, sim: discord.Option(name= "simulator", choises=sim_types, autocomplete= autocomplete_sims), plane: discord.Option(name="plane", input_type=str)):
		with open("/root/thomascook/links.json", "r") as f:
			data = json.load(f)
		try:
			await ctx.respond(f"Симулятор: {sim}\nМодель: {plane}\nСсылка: {data['scenery'][sim][plane]}")
		except:
			await ctx.respond("Что то пошло не так... Такой самолет небыл найден!")


def setup(bot):
	bot.add_cog(CloudCommands(bot))
	print("CloudCommands loaded!")