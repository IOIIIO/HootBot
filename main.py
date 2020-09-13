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


"""
tweet is only used when we want to archive the text from a tweet or embed
"""

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


"""
Used to setup the bot.
"""






"""
Change default prefix.
"""
	

"""
Toggle whether cache should be used.
"""



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


"""
Overrides the image that was going to the archived originally.
"""


bot.run(cfg['token'])
