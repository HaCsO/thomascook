from .__utils import *
from .__virtaparser import *
import discord
from discord.ext import commands, tasks
import os
import json
from datetime import timedelta

class Statistics(commands.Cog):
	stats_channel = 798224036977967126
	def __init__(self, bot):
		self.bot = bot
		
	@commands.Cog.listener()
	async def on_ready(self):
		self.statistics_update.start()

	@is_approved_channel()
	@commands.slash_command()
	async def profile(self, ctx, name):
		prf = Flighter(name)
		try:
			prf.update_user()
		except:
			await ctx.respond("Указанный пользователь не найден!")
		await ctx.respond(prf.account_card_image)

	@tasks.loop(hours=1)
	async def statistics_update(self):
		cache = self.check_cached_msgs()
		if not cache:
			await self.send_stat_msgs()
			return
		if len(cache.keys()) < 3:
			await self.delete_messages(cache)
			await self.send_stat_msgs()
			return
		
		await self.update_messages(cache)

	async def delete_messages(self, cache):
		for i in cache.values():
			msg = await self.bot.get_channel(self.stats_channel).fetch_message(i)
			await msg.delete()

		await self.purge_cache()

	async def update_messages(self, cache):
		f = FlightCompany("Thomas Cook Airlines")
		amount, miles, time = f.get_all_tops_formated()
		msg = await self.bot.get_channel(self.stats_channel).fetch_message(cache["amount"])
		emb = msg.embeds[0]
		emb.description = "\n".join([f"{place}. {flighter.username} = **{val}**" for place, (flighter, val) in enumerate(amount.items(), 1)])
		await msg.edit(embed = emb)
		msg = await self.bot.get_channel(self.stats_channel).fetch_message(cache["miles"])
		emb = msg.embeds[0]
		emb.description = "\n".join([f"{place}. {flighter.username} = **{val} nM**" for place, (flighter, val) in enumerate(miles.items(), 1)])
		await msg.edit(embed = emb)
		msg = await self.bot.get_channel(self.stats_channel).fetch_message(cache["time"])
		emb = msg.embeds[0]
		emb.description = "\n".join([f"{place}. {flighter.username} = **{strfdelta(timedelta(seconds=val), '{H}h:{M}m:{S}s')}**" for place, (flighter, val) in enumerate(time.items(), 1)])
		await msg.edit(embed = emb)

	async def send_stat_msgs(self):
		f = FlightCompany("Thomas Cook Airlines")
		amount, miles, time = f.get_all_tops_formated()
		chan = self.bot.get_channel(self.stats_channel)
		if not chan:
			return False
		emb = discord.Embed(title="Топ по количеству полётов", description= "\n".join(
			[f"{place}. {flighter.username} = **{val}**" for place, (flighter, val) in enumerate(amount.items(), 1)]
			), color=discord.Color.orange())
		self.write_cache("amount", (await chan.send(embed=emb)).id)
		emb = discord.Embed(title="Топ по количеству пройденного расстояния", description= "\n".join(
			[f"{place}. {flighter.username} = **{val} nM**" for place, (flighter, val) in enumerate(miles.items(), 1)]
			), color=discord.Color.orange())
		self.write_cache("miles", (await chan.send(embed=emb)).id)
		emb = discord.Embed(title="Топ по общему времени полёта", description= "\n".join(
			[f"{place}. {flighter.username} = **{strfdelta(timedelta(seconds=val), '{H}h:{M}m:{S}s')}**" for place, (flighter, val) in enumerate(time.items(), 1)]
			), color=discord.Color.orange())
		self.write_cache("time", (await chan.send(embed=emb)).id)

	def check_cached_msgs(self):
		cache = None
		try:
			with open("/root/thomascook/cache.json", "r") as f:
				cache = json.load(f)
		except:
			return False
		return cache
	
	def write_cache(self, topname, message_id):
		msg = self.check_cached_msgs() or {}
		msg[topname] = message_id
		with open("/root/thomascook/cache.json", "w") as f:
			json.dump(msg, f)

	def purge_cache(self):
		with open("/root/thomascook/cache.json", "w") as f:
			json.dump({}, f)

def setup(bot):
	print("Statistics loaded!")
	bot.add_cog(Statistics(bot))