import discord
from discord.ext import commands, tasks
import os
import json
import requests
from bs4 import BeautifulSoup

class VirtAirLinesStatistics():
	def __init__(self):
		self.domain = "http://www.virtairlines.ru/"

	def get_data(self, address):
		return BeautifulSoup(requests.get(f"{self.domain}{address}").content, "html.parser")

class FlightCompany(VirtAirLinesStatistics):
	name = None
	def __init__(self, name):
		super().__init__()
		self.name = name

	def get_all_members(self, name = None):
		if not name:
			name = self.name
		assert name != None

		soup = self.get_data(f"db/{name}")
		members_table = soup.find_all("table", {"cellspacing": "2", "width": "860"})[2]
		members_table = members_table.find_all("tr")
		pilots = []
		for i in range(2, len(members_table)):
			pilots.append(members_table[i].contents[3].text)		
		return pilots
	
	def get_all_members_obj(self, name = None):
		if not name:
			name = self.name
		assert name != None

		members = []
		for i in self.get_all_members():
			mbr = Flighter(i)
			mbr.update_user()
			members.append(mbr)
		return members

	def get_top_by_of(self, typeofsort, members = None, name = None):
		if not members:
			members = self.get_all_members_obj()
		if not name:
			name = self.name
		assert name != None
		members_dict = {}
		for member in members:
			members_dict[member] = int(member.general_table[typeofsort]["text"])

		return {k: v for k, v in sorted(members_dict.items(), key=lambda item: item[1], reverse=True)}
	
	def get_top_by_amount(self, name= None, members = None):
		self.get_top_by_of("Количество полётов:", name, members)

	def get_top_by_miles(self, name= None, members = None):
		self.get_top_by_of("Расстояние налёта:", name, members)

	def get_top_by_time(self, name= None, members = None):
		self.get_top_by_of("Часы налёта:", name, members)

	def get_all_tops_formated(self, name = None):
		members = self.get_all_members_obj()
		top_by_amount = self.get_top_by_amount(members = members)
		top_by_miles = self.get_top_by_miles(members= members)
		top_by_time = self.get_top_by_time(members= members)

		return top_by_amount, top_by_miles, top_by_time

class Flighter(VirtAirLinesStatistics):
	username = None
	general_table = {}
	account_image = None
	account_card_image = None
	def __init__(self, name):
		super().__init__()
		self.username = name

	def format_time(self):
		if not self.general_table["Часы налёта:"]["text"]:
			return
		time = self.general_table["Часы налёта:"]["text"][:-2].split(":")
		time = int(time[0])*(60**2) + int(time[1]) * 60 + int(time[2])
		self.general_table["Часы налёта:"]["text"] = time

	def format_miles(self):
		if not self.general_table["Расстояние налёта:"]["text"]:
			return

		self.general_table["Расстояние налёта:"]["text"] = self.general_table["Расстояние налёта:"]["text"][:-3]

	def update_user(self, user = None):
		if not user:
			user = self.username
		assert user != None

		soup = self.get_data(f"db/{user}")

		imgs = soup.find_all("img", {"title": user})

		self.account_image = self.domain + imgs[0].attrs["src"].replace("../", "")
		self.account_card_image = self.domain + imgs[1].attrs["src"].replace("../", "")

		name = soup.find_all("td", {"class": "content_of_form"})
		res = soup.find_all("td", {"class": "info_tbl_titles"})
		for i in range(min(len(name), len(res))):
			img = res[i].find('img')
			img = f"{self.domain[:-1]}{img.attrs['src'].replace('../', '/')}" if img else None
			self.general_table[name[i].text] = {"text": res[i].text.replace("\xa0", ""), "add": img}

		self.format_miles()
		self.format_time()

class Statistics(commands.Cog):
	stats_channel = 798224036977967126
	def __init__(self, bot):
		self.bot = bot

	@tasks.loop(hours=1)
	async def statistics_update(self):
		if not self.check_cached_msgs():
			...	

	async def send_stat_msgs(self):
		amount, miles, time = FlightCompany.get_all_tops_formated("Thomas Cook Airlines")
		chan = self.bot.get_channel(self.stats_channel)
		if not chan:
			return False
		
		emb = discord.Embed(title="Топ по количеству полётов", description= "\n".join(
			[f"{place}. {name} = {val}" for place, (name, val) in enumerate(amount.items(), 1)]
			))

	def check_cached_msgs(self):
		cache = None
		try:
			with open(os.getcwd() + "cache.json", "r") as f:
				cache = json.load(f)
		except:
			return False
		return cache
	
	def write_cache(self, topname, message_id):
		msg = self.check_cached_msgs()
		msg[topname] = message_id
		with open(os.getcwd() + "cache.json", "wb") as f:
			json.dump(msg, f)

def setup(bot):
	bot.add_cog(Statistics(bot))