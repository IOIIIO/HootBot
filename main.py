import json
import os
import re
import sys
from urllib.parse import parse_qs, urlparse, quote_plus
import urllib.request
import datetime
import time

try:
	import discord
	from discord.ext import commands
	from bs4 import BeautifulSoup
	import requests
	from imgurpython import ImgurClient
	import praw
except:
	sr()

if os.path.isfile("bot.json"):
	cfg = json.load(open('bot.json'))
else:
	sc()
	cfg = json.load(open('bot.json'))


exceptions = []


"""
tweet is only used when we want to archive the text from a tweet or embed
"""


bot = commands.Bot(command_prefix=cfg["config"]["prefix"], owner=cfg["owner"])

@bot.event
async def on_ready():
	print('Logged in as {}'.format(bot.user.name))
	if cfg["config"] and cfg["config"]["reddit_id"] and cfg["config"]["reddit_scr"] != "":
		print('Logged into Reddit as {}'.format(reddit.user.me()))
	
	if cfg["config"] and cfg["config"]["presence"] and cfg['config']["presence"] != "":
		await bot.change_presence(activity=discord.Game(name=cfg["config"]['presence']))

"""
I use on_raw_reaction_add instead of on_reaction_add, because on_reaction_add doesn't work with messages that were sent before the bot went online.
"""


async def redembed(message):
	if cfg[str(message.guild.id)]['reddit'] == True:
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
				if url != []:
					url2 = re.sub(r'\?.*', "", url[0][0])
					if "reddit.com" in url2 or "redd.it" in url2:
						try:
							b = return_reddit(url2)
							if b != '':
								embed=discord.Embed(title="Reddit Embed", description=message.content)
								embed.add_field(name='Sender', value=str(message.author))
								embed.set_image(url=b)
								await message.channel.send(embed=embed)
						except:
							pass

async def insta(message):
	if cfg[str(message.guild.id)]['insta'] == True:
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
				if url != []:
					if "instagram.com" in url[0][0]:
						embed=discord.Embed(title="Instagram Embed", description=message.content)
						embed.add_field(name='Sender', value=str(message.author))
						embed.set_image(url=BeautifulSoup(requests.get(url[0][0].replace('mobile.', '')).text, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'))
						await message.channel.send(embed=embed)

@bot.event
async def on_message(message):
	if not isinstance(message.channel, discord.channel.DMChannel):
		if 'insta' in cfg[str(message.guild.id)]:
			await insta(message)

		if 'reddit' in cfg[str(message.guild.id)]:
			await redembed(message)

	await bot.process_commands(message)

def is_owner(ctx):
	if str(ctx.message.author.id) == cfg["owner"]:
		return True
	else:
		return False

"""
Used to setup the bot.
"""
@bot.command(brief='Sets up the bot.')
@commands.has_permissions(administrator=True)
async def setup(ctx, archive_channel: discord.TextChannel, archive_emote: discord.Emoji, archive_emote_amount: int):
	if str(ctx.guild.id) in cfg:
		return
	
	cfg[str(ctx.guild.id)] = {
		'ignore_list': [],
		'bot': {
			'archive_channel': archive_channel.id,
        	'archive_emote': str(archive_emote),
        	'archive_emote_amount': archive_emote_amount,
		}
	}
	json.dump(cfg, open('bot.json', 'w'), indent=4)

@bot.command(help="Sets the amount of emotes required for a message to reach starboard.", brief='Change the emote amount requirement.')
@commands.has_permissions(administrator=True)
async def setamount(ctx, b: int):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Server not in config. Use setup command first.")
	else:
		cfg[str(ctx.guild.id)]["bot"]['archive_emote_amount'] = b
	await ctx.send("Succesfully changed amount to {}".format(b))
	json.dump(cfg, open('bot.json', 'w'), indent=4)



"""
Change default prefix.
"""


"""
Toggle whether cache should be used.
"""
@bot.group(brief='Toggle whether cache should be used.')
async def cache(ctx):
	if ctx.invoked_subcommand is None:
		if is_owner(ctx):
			if "cache" in cfg["config"]:
				if cfg["config"]["cache"] == True:
					cfg["config"].update({'cache' : False})
					b = "disabled"
				else:
					cfg["config"].update({'cache' : True})
					b = "enabled"
			else:
				cfg["config"].update({'cache' : True})
				b = "enabled"
			json.dump(cfg, open('bot.json', 'w'), indent=4)
			await ctx.send("Succesfully changed cache state to: \"{}\"".format(b))

@cache.command(brief='Set imgur UserID.')
async def user(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'imgur_usr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@cache.command(brief='Set imgur Secret.')
async def secret(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'imgur_scr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@bot.command(brief='Set twitter bearer.')
async def twitter(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'twitter' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated bearer key.")
	b = 0
"""
Toggle automatic Instagram embeds.
"""

@bot.group(brief="Allow bot to embed images which are normally broken")
async def embed(ctx):
	pass

@embed.group(brief='Toggle automatic Instagram embeds.')
@commands.has_permissions(administrator=True)
async def instagram(ctx):
	if "insta" in cfg[str(ctx.message.guild.id)]:
		if cfg[str(ctx.message.guild.id)]["insta"] == True:
			cfg[str(ctx.message.guild.id)].update({'insta' : False})
			b = "disabled"
		else:
			cfg[str(ctx.message.guild.id)].update({'insta' : True})
			b = "enabled"
	else:
		cfg[str(ctx.message.guild.id)].update({'insta' : True})
		b = "enabled"
	json.dump(cfg, open('bot.json', 'w'), indent=4)
	await ctx.send("Succesfully changed embed state to: \"{}\"".format(b))

@embed.group(name="reddit", brief="Configure reddit embed settings")
async def redd(ctx):
	pass
	
@commands.has_permissions(administrator=True)
@redd.command(brief='Toggle automatic Reddit embeds.')
async def enable(ctx):
	if "reddit" in cfg[str(ctx.message.guild.id)]:
		if cfg[str(ctx.message.guild.id)]["reddit"] == True:
			cfg[str(ctx.message.guild.id)].update({'reddit' : False})
			b = "disabled"
		else:
			cfg[str(ctx.message.guild.id)].update({'reddit' : True})
			b = "enabled"
	else:
		cfg[str(ctx.message.guild.id)].update({'reddit' : True})
		b = "enabled"
	json.dump(cfg, open('bot.json', 'w'), indent=4)
	await ctx.send("Succesfully changed embed state to: \"{}\"".format(b))

@redd.command(brief='Set Reddit ID.')
async def id(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_id' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@redd.command(brief='Set Reddit Secret.')
async def secret(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_scr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@redd.command(brief='Set Reddit Token.')
async def token(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_tkn' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

"""
Update the bot and restarts
"""


"""
Print neofetch in chat
"""


"""
Show when the next episode of the show will air.
"""



"""
Deletes the given message from archive cache.
"""
@bot.command(brief='Removes the given message from the archive cache.')
@commands.has_permissions(administrator=True)
async def del_entry(ctx, msglink: str):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		return

	msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
	"""
	msg_data[0] -> server id
	msg_data[1] -> channel id
	msg_data[2] -> msg id
	"""

	cfg[ctx.guild.id]['ignore_list'].remove(str(msg_data[1])+str(msg_data[2]))
	json.dump(cfg, open('bot.json', 'w'), indent=4)


"""
Overrides the image that was going to the archived originally.
"""
@bot.command(brief='Overrides the image that was going to the archived originally.')
@commands.has_permissions(administrator=True)
async def override(ctx, msglink: str, link: str):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		return
		
	msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
	"""
	msg_data[0] -> server id
	msg_data[1] -> channel id
	msg_data[2] -> msg id
	"""

	if msg_data[1] + msg_data[2] not in exceptions:
		exceptions.append(msg_data[1] + msg_data[2])

bot.run(cfg['token'])
