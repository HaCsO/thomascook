import aiohttp
from bs4 import BeautifulSoup
from configparser import ConfigParser
cfg = ConfigParser()
cfg.read("./config.cfg")

class VirtAirLinesStatistics(object):
	def __init__(self):
		self.domain = "http://www.virtairlines.ru/"
		self.login_params_template = {
			"email": cfg["virtairlines"]["login"],
			"pass": cfg["virtairlines"]["pass"],
			"blue": "Войти",
			"send_action": "login"
		}

	async def get_data(self, address, given_session = None, login=False):
		if not given_session:
			session = aiohttp.ClientSession()
		else:
			session = given_session

		if login:
			await session.post(self.domain, data= self.login_params_template)

		async with session.get(f"{self.domain}{address}") as data:
			bs = BeautifulSoup(await data.text(), "html.parser")
		if not given_session:
			await session.close()
		return bs

class FlightCompany(VirtAirLinesStatistics):
	name = None
	def __init__(self, name):
		super().__init__()
		self.name = name



	async def get_main_info_table(self, name = None):
		if not name:
			name = self.name
		assert name != None

		soup = await self.get_data(f"db/{name}")
		return soup.find_all("table", {"cellspacing": "2", "width": "480"})[0]

	async def get_balance(self, name = None):
		return (await self.get_main_info_table(name)).find_all("tr")[6].contents[3].text

	async def get_rax_rep(self, name = None):
		return (await self.get_main_info_table(name)).find_all("tr")[7].contents[3].text


	async def get_all_members(self, name = None):
		if not name:
			name = self.name
		assert name != None

		soup = await self.get_data(f"db/{name}")
		members_table = soup.find_all("table", {"cellspacing": "2", "width": "860"})[2]
		members_table = members_table.find_all("tr")
		pilots = []
		for i in range(2, len(members_table)):
			pilots.append(members_table[i].contents[3].text)		
		return pilots
	
	async def get_all_members_obj(self, name = None):
		if not name:
			name = self.name
		assert name != None

		members = []
		for i in await self.get_all_members():
			mbr = Flighter(i)
			await mbr.update_user()
			members.append(mbr)
			mbr = None
		return members

	async def get_top_by_of(self, typeofsort, name = None, members = None):
		if not members:
			members = await self.get_all_members_obj()
		if not name:
			name = self.name
		assert name != None
		members_dict = {}
		for member in members:
			members_dict[member] = int(float(member.general_table[typeofsort]["text"]))

		return {k: v for k, v in sorted(members_dict.items(), key=lambda item: item[1], reverse=True)}
	
	async def get_top_by_amount(self, name= None, members = None):
		return await self.get_top_by_of("Количество полётов:", name, members)

	async def get_top_by_miles(self, name= None, members = None):
		return await self.get_top_by_of("Расстояние налёта:", name, members)

	async def get_top_by_time(self, name= None, members = None):
		return await self.get_top_by_of("Часы налёта:", name, members)

	async def get_top_by_rating(self, name= None, members = None):
		return await self.get_top_by_of("Полётный рейтинг:", name, members)

	async def get_all_tops_formated(self, name = None):
		members = await self.get_all_members_obj()
		top_by_amount = await self.get_top_by_amount(members = members)
		top_by_miles = await self.get_top_by_miles(members= members)
		top_by_time = await self.get_top_by_time(members= members)
		top_by_rating = await self.get_top_by_rating(members= members)

		return top_by_amount, top_by_miles, top_by_time, top_by_rating

class Flighter(VirtAirLinesStatistics):
	def __init__(self, name):
		super().__init__()
		self.username = name
		self.general_table = {}
		self.account_image = None
		self.account_card_image = None

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

	async def update_user(self, user = None):
		if not user:
			user = self.username
		assert user != None

		soup = await self.get_data(f"db/{user}")

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
