from .__utils import *
from .__virtaparser import *
import discord
from discord.ext import commands, tasks
import os
import json
from datetime import timedelta, datetime
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt
import io
import numpy
import matplotlib.dates as mdates

class Statistics(commands.Cog):
	stats_channel = 866564068603854848
	stats_len = 6
	def __init__(self, bot):
		self.bot = bot
		self.cmpname = "Thomas Cook Airlines"

	@commands.Cog.listener()
	async def on_ready(self):
		self.grep_statistics.start()
		self.statistics_update.start()

	@is_approved_channel()
	@commands.slash_command()
	async def profile(self, ctx, name):
		prf = Flighter(name)
		try:
			await prf.update_user()
		except:
			await ctx.respond("Указанный пользователь не найден!")
		await ctx.respond(prf.account_card_image)

	@tasks.loop(hours=24)
	async def grep_statistics(self):
		f = FlightCompany(self.cmpname)
		balance = int((await f.get_balance())[:-2].replace(".", ""))
		rep = float(await f.get_rax_rep())
		db = sqlite3.connect("/root/thomascook/statistics.db")
		cur = db.cursor()
		timestamp = datetime.now().timestamp()
		cur.execute(f"INSERT INTO balance VALUES ({timestamp}, {balance})")
		cur.execute(f"INSERT INTO rating VALUES ({timestamp}, {rep})")
		cur.close()
		db.commit()
		db.close()

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
			try:
				await self.update_messages(cache)
			except:
				self.purge_cache()
				await self.send_stat_msgs()

		await self.bot.change_presence(activity=WatchingAct())

	async def delete_messages(self, cache):
		for i in cache.values():
			try:
				msg = await self.bot.get_channel(self.stats_channel).fetch_message(i)
				await msg.delete()
			except:
				continue

		self.purge_cache()

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
		f = FlightCompany(self.cmpname)
		amount, miles, time, rating = await f.get_all_tops_formated()

		await self._update_message(cache["amount"], amount, lambda x: x)
		await self._update_message(cache["miles"], miles, lambda x: f"{x} nM")
		await self._update_message(cache["time"], time, lambda x: f"{strfdelta(timedelta(seconds=x), '{H}h:{M}m:{S}s')}")
		await self._update_message(cache["rating"], rating, lambda x: x)
		await (await self.bot.get_channel(self.stats_channel).fetch_message(cache["balance_graf"])).edit(attachments= [], file= await self.get_plot_image("balance", "Тугрики"))
		await (await self.bot.get_channel(self.stats_channel).fetch_message(cache["rating_graf"])).edit(attachments= [], file = await self.get_plot_image("rating", "Рерутация"))


	async def _send_stat_msgs_and_cache(self, channel, name, title, lst, formatter):
		emb = discord.Embed(title=title, description= self.format_desc(lst, formatter), color=discord.Color.orange())
		dtformat = datetime.now()
		dtformat = dtformat.strftime("%Y.%m.%d %H:%M")
		emb.set_footer(text=f"Последнее обновление: {dtformat}")
		self.write_cache(name, (await channel.send(embed=emb)).id)

	async def send_stat_msgs(self):
		f = FlightCompany(self.cmpname)
		amount, miles, time, rating = await f.get_all_tops_formated()
		chan = self.bot.get_channel(self.stats_channel)
		if not chan:
			return False

		await self._send_stat_msgs_and_cache(chan, "amount", "Топ по количеству полётов", amount, lambda x: x)
		await self._send_stat_msgs_and_cache(chan, "miles", "Топ по количеству пройденного расстояния", miles, lambda x: f"{x} nM")
		await self._send_stat_msgs_and_cache(chan, "time", "Топ по общему времени полёта", time, lambda x: f"{strfdelta(timedelta(seconds=x), '{H}h:{M}m:{S}s')}")
		await self._send_stat_msgs_and_cache(chan, "rating", "Топ полётного рейтинга", rating, lambda x: x)
		msg = await chan.send(file= await self.get_plot_image("balance", "Тугрики"))
		self.write_cache("balance_graf", msg.id)
		msg = await chan.send(file= await self.get_plot_image("rating", "Репутация"))
		self.write_cache("rating_graf", msg.id)

	async def get_plot_image(self, tablename: str, lehend_label = None):
		db = sqlite3.connect("/root/thomascook/statistics.db")
		cur = db.cursor()
		cur.execute(f"SELECT * FROM {tablename} ORDER BY dt ASC LIMIT 30")
		data = cur.fetchall()
		cur.close()
		db.close()
		
		fig, ax = plt.subplots(constrained_layout=True)
		fig.set_size_inches(18.5, 5.5)
		ax.set_title(f"Статистика значения: {tablename}")
		ax.set_xlabel("Date")
		ax.set_ylabel(tablename.capitalize())
		ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

		x, y = map(list,zip(*data))
		dates = [datetime.fromtimestamp(float(i)).strftime("%m.%d") for i in x]

		ax.plot(dates, y, label=lehend_label)
		ax.legend()

		buff = io.BytesIO()
		fig.savefig(buff, format="png", dpi=200)
		buff.seek(0)
		return discord.File(buff, filename="statistics.png")

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