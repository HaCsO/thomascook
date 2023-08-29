from .__utils import *
from .__virtaparser import *
import discord
from discord.ext import commands, tasks
import os
import json
from datetime import timedelta, datetime

class Statistics(commands.Cog):
	stats_channel = 798224036977967126
	stats_len = 4
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
		await self.bot.change_presence(activity=discord.Game(name="статистику"), status=discord.Status.dnd)
		cache = self.check_cached_msgs()
		if not cache:
			await self.send_stat_msgs()
		elif len(cache.keys()) < self.stats_len:
			await self.delete_messages(cache)
			await self.send_stat_msgs()
		else:
			await self.update_messages(cache)
		await self.bot.change_presence(activity=WatchingAct())

	async def delete_messages(self, cache):
		for i in cache.values():
			msg = await self.bot.get_channel(self.stats_channel).fetch_message(i)
			await msg.delete()

		await self.purge_cache()

	def format_desc(self, lst, formatter):
		return "\n".join([f"{place}. {flighter.username} = **{formatter(val)}**" for place, (flighter, val) in enumerate(lst.items(), 1)])

	async def _update_message(self, msg_id, lst, formatter):
		msg = await self.bot.get_channel(self.stats_channel).fetch_message(msg_id)
		emb = msg.embeds[0]
		emb.description = self.format_desc(lst, formatter)
		dtformat = datetime.now()
		dtformat = dtformat.strftime("%Y.%m.%d %H:%M")
		emb.set_footer(text=f"Последнее обновление: {dtformat}")
		await msg.edit(embed = emb)

	async def update_messages(self, cache):
		f = FlightCompany("Thomas Cook Airlines")
		amount, miles, time, rating = f.get_all_tops_formated()

		await self._update_message(cache["amount"], amount, lambda x: x)
		await self._update_message(cache["miles"], miles, lambda x: f"{x} nM")
		await self._update_message(cache["time"], time, lambda x: f"{strfdelta(timedelta(seconds=x), '{H}h:{M}m:{S}s')}")
		await self._update_message(cache["rating"], rating, lambda x: x)

	async def _send_stat_msgs_and_cache(self, channel, name, title, lst, formatter):
		emb = discord.Embed(title=title, description= self.format_desc(lst, formatter), color=discord.Color.orange())
		dtformat = datetime.now()
		dtformat = dtformat.strftime("%Y.%m.%d %H:%M")
		emb.set_footer(text=f"Последнее обновление: {dtformat}")
		self.write_cache(name, (await channel.send(embed=emb)).id)

	async def send_stat_msgs(self):
		f = FlightCompany("Thomas Cook Airlines")
		amount, miles, time, rating = f.get_all_tops_formated()
		chan = self.bot.get_channel(self.stats_channel)
		if not chan:
			return False

		await self._send_stat_msgs_and_cache(chan, "amount", "Топ по количеству полётов", amount, lambda x: x)
		await self._send_stat_msgs_and_cache(chan, "miles", "Топ по количеству пройденного расстояния", miles, lambda x: f"{x} nM")
		await self._send_stat_msgs_and_cache(chan, "time", "Топ по общему времени полёта", time, lambda x: f"{strfdelta(timedelta(seconds=x), '{H}h:{M}m:{S}s')}")
		await self._send_stat_msgs_and_cache(chan, "rating", "Топ полётного рейтинга", rating, lambda x: x)

	def check_cached_msgs(self):
		cache = None
		try:
			with open(os.getcwd() + "/cache.json", "r") as f:
				cache = json.load(f)
		except:
			return False
		return cache
	
	def write_cache(self, topname, message_id):
		msg = self.check_cached_msgs() or {}
		msg[topname] = message_id
		with open(os.getcwd() + "/cache.json", "w") as f:
			json.dump(msg, f)

	def purge_cache(self):
		with open(os.getcwd() + "/cache.json", "w") as f:
			json.dump({}, f)

def setup(bot):
	print("Statistics loaded!")
	bot.add_cog(Statistics(bot))