from discord.ext import commands
from string import Formatter
import discord

channel_list = [
	867298168492261376,
	686598604340592640,
	798224036977967126
]

def is_approved_channel():
	def predicate(ctx):
		return ctx.channel.id in channel_list

	return commands.check(predicate) 


def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
	# Convert tdelta to integer seconds.
	if inputtype == 'timedelta':
		remainder = int(tdelta.total_seconds())
	elif inputtype in ['s', 'seconds']:
		remainder = int(tdelta)
	elif inputtype in ['m', 'minutes']:
		remainder = int(tdelta)*60
	elif inputtype in ['h', 'hours']:
		remainder = int(tdelta)*3600
	elif inputtype in ['d', 'days']:
		remainder = int(tdelta)*86400
	elif inputtype in ['w', 'weeks']:
		remainder = int(tdelta)*604800

	f = Formatter()
	desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
	possible_fields = ('W', 'D', 'H', 'M', 'S')
	constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
	values = {}
	for field in possible_fields:
		if field in desired_fields and field in constants:
			values[field], remainder = divmod(remainder, constants[field])
	return f.format(fmt, **values)

class WatchingAct(discord.BaseActivity):
	def to_dict(self) -> discord.Activity:
		return {"type": 3, "name": "прямо в душу"}

class Table:
	def __init__(self, cmpname):
		self.cmpname = cmpname
		self.strings = []
		self.cmp_index = 0

	def parse_trs(self, bs):
		for str in bs:
			t = str.text.split("\n")
			tstr = TableString(int(t[1][:-1]), t[2], float(t[3]))
			self.strings.append(tstr)
			if t[2] == self.cmpname:
				self.cmp_index = int(t[1][:-1])-1
class TableString:
	def __init__(self, number, name, points):
		self.number = number
		self.name = name
		self.points = points
		