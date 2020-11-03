import discord
from discord.ext import commands
import cogs.support.db as dbc
import cogs.support.reddit as rdc
import sys, os, re, json
from bs4 import BeautifulSoup
import requests
from urllib.parse import parse_qs, urlparse, quote_plus
import cogs.support.db as dbc
import cogs.support.perms as perms
import ast
import cogs.derpi as derpi

class Starboard(commands.Cog, name="Starboard Commands"):
	"""Commands related to controlling the starboard."""
	def __init__(self, bot):
		self.bot = bot
		self.exceptions = []
		self.s = dbc.db["starboardServers"]
		self.o = dbc.db["starboardOverrides"]
		self.i = dbc.db["starboardIgnore"]
		if dbc.db["starboardServers"] is None:	
			try:
				dbc.db.query('CREATE TABLE starboardOverrides (channel_id,channel_am);')
				dbc.db.query('CREATE TABLE starboardServers (archive_channel,archive_emote,archive_emote_amount,server_id,);')
				dbc.db.query('CREATE TABLE starboardIgnore (id, server_id);')
				print("Successfully created starboard tables.")
			except:
				print("Failed. Perhaps starboard tables already exist?")

	# https://stackoverflow.com/a/45579374
	def __get_id(self, url): 
		# Grabs the ID of the YouTube video to use for thumbnail.
		# url = link to be processed by function
		u_pars = urlparse(url)
		quer_v = parse_qs(u_pars.query).get('v')
		if quer_v:
			return quer_v[0]
		pth = u_pars.path.split('/')
		if pth:
			return pth[-1]

	async def __buildEmbed(self, msg, url, tweet = '', author = '', link = ''):
		# Builds embed, archives image, and posts image to archive.
		# msg = callback to message being archived
		# url = direct link to image to be archived (optional)
		# tweet = string to be posted in Content field of embed
		# author = pre-set author of original message. Overrides author of msg
		# link = link to the source post of the archived image
		if url != "":
			if int(dbc.ret("bot", "archive")) == 1: # Check if archive is globally enabled
				try:
					url2 = url # Set a backup, in case the next function screws up the link
					if any(ext in url for ext in ['.gif', ".jpg", ".webm", ".jpeg", ".png", ".svg"]):
						b = await derpi.post(str(link), str(url))
						url = dbc.ret("bot", "archiveLink") + b["image"]["representations"]["full"]
					else:
						url = url2 # Fallback to backup, just in case
						pass
				except:
					url = url2
					pass
		embed = discord.Embed()
		if len(tweet):
			embed.add_field(name='Tweet/Embed Content', value=tweet, inline=False)
		elif isinstance(msg, discord.Message) and len(msg.content):
			embed.add_field(name='Content', value=msg.content, inline=False)
		embed.add_field(name='Message Link', value='https://discordapp.com/channels/{}/{}/{}'.format(msg.guild.id, msg.channel.id, msg.id), inline=False)
		if len(author):
			auth = author
		else:
			auth = msg.author.mention
		embed.add_field(name='Author', value=auth, inline=True)
		embed.add_field(name='Channel', value=msg.channel.mention, inline=True)
		embed.set_image(url=url)

		await self.bot.get_channel(int(self.s.find_one(server_id=msg.guild.id)['archive_channel'])).send(embed=embed)

	def arrs(self, value, msg, type=True):
		# Writes to the table of ignored (archived) messages
		# value = unique ID of message consisting of a concatenation of message snowflake and channel snowflake 
		# msg = callback to message being archived (or if type is false, the ID of the guild the message comes from)
		# type = sets add/delete mode. True is add, False is delete 
		if type == True:
			c = msg.guild.id
		elif type == False:
			c = int(msg) # ID is passed by the caller
		try:
			if type == True:
				self.i.insert(dict(id=value, server_id=c))
			elif type == False:
				self.i.delete(id=value, server_id=c)
		except:
			return None

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		# Main function sorting messages and extracting images
		# payload = indirect callback to message being archived 
		msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id) # Only call function if set up
		if not self.s.find_one(server_id=msg.guild.id):
			return

		for reaction in msg.reactions:
			if type(reaction.emoji) != str and reaction.emoji.id == int(self.s.find_one(server_id=msg.guild.id)['archive_emote']):
				if self.i.find_one(id=str(payload.channel_id)+str(payload.message_id)) is not None: # Verify if message isn't already archived
					return
				state = False
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', msg.content)
				if url:
					if 'dcinside.com' in url[0][0] and not msg.attachments: # Unsupported website
						await self.bot.get_channel(payload.channel_id).send('https://discordapp.com/channels/{}/{}/{} not supported, please attach the image that you want to archive to the link.'.format(msg.guild.id, msg.channel.id, msg.id))

						self.arrs(str(payload.channel_id)+str(payload.message_id), msg)
						return
				if self.o.find_one(channel_id=msg.channel.id) != None: # Check if channel has a value override
					if reaction.count >= int(self.o.find_one(channel_id=msg.channel.id)["channel_am"]): # Verify if reaction threshold is met
						state = True
				elif reaction.count >= int(self.s.find_one(server_id=msg.guild.id)['archive_emote_amount']): # Verify if reaction threshold is met
					state = True
				if state == True:
					if str(payload.channel_id)+str(payload.message_id) in self.exceptions: # Check if message is in exceptions list, and if so use the pre-set image
						await self.__buildEmbed(msg, self.exceptions[str(payload.channel_id)+str(payload.message_id)])

						self.exceptions.remove(str(payload.channel_id)+str(payload.message_id))
					else:
						self.arrs(str(payload.channel_id)+str(payload.message_id), msg) # Add image to archived list
						if url:
							if msg.attachments:
								await self.__buildEmbed(msg, msg.attachments[0].url, link=url[0][0])
							else:
								processed_url = requests.get(url[0][0].replace('mobile.', '')).text
								"""
								most sites that can host images, put the main image into the og:image property, so we get the links to the images from there
								<meta property="og:image" content="link" />
								"""
								if 'deviantart.com' in url[0][0] or 'www.instagram.com' in url[0][0] or 'tumblr.com' in url[0][0] or 'pixiv.net' in url[0][0]:
									await self.__buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'), link=url[0][0])
								elif 'twitter.com' in url[0][0]:
									if dbc.ret("bot", "twitter") != None: # Verify if authentication is setup.
										try:
											res = json.loads(requests.get('https://api.twitter.com/1.1/statuses/lookup.json?id={}&tweet_mode=extended'.format(re.findall(r'.*?twitter\.com\/.*?\/status\/(\d*).*?', url[0][0])[0]), headers={"Authorization": "Bearer {}".format(dbc.ret("bot", "twitter"))}).text)
										except:
											return
										if 'user' in res[0]:
											if 'media' in res[0]['entities']: # Check if Tweet contains image. If not, embed text.
												await self.__buildEmbed(msg, res[0]["entities"]["media"][0]["media_url"], link=url[0][0])
											else:
												await self.__buildEmbed(msg, "", res[0]["full_text"])
										else:
											print(res)
								elif 'youtube.com' in url[0][0] or 'youtu.be' in url[0][0]:
									await self.__buildEmbed(msg, 'https://img.youtube.com/vi/{}/0.jpg'.format(self.__get_id(url[0][0])), link=url[0][0])
								elif 'dcinside.com' in url[0][0]:
									await self.__buildEmbed(msg, msg.attachments[0].url)
								elif 'imgur' in url[0][0]:
									if 'i.imgur' not in url[0][0]:
										await self.__buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content').replace('?fb', ''), link=url[0][0])
									else:
										await self.__buildEmbed(msg, url[0][0])
								elif 'https://tenor.com' in url[0][0]:
									for img in BeautifulSoup(processed_url, 'html.parser').findAll('img', attrs={'src': True}):
										if 'media1.tenor.com' in img.get('src'):
											await self.__buildEmbed(msg, img.get('src'), link=url[0][0])
								elif "reddit.com" in url[0][0] or "redd.it" in url[0][0]:
									await self.__buildEmbed(msg, rdc.return_reddit(url[0][0]), link=url[0][0])
								else:
									if msg.embeds and msg.embeds[0].url != url[0][0]:
										await self.__buildEmbed(msg, msg.embeds[0].url)
									else:
										if msg.attachments:
											await self.__buildEmbed(msg, msg.attachments[0].url)
										else:
											await self.__buildEmbed(msg, '')
						else:
							if msg.attachments:
								await self.__buildEmbed(msg, msg.attachments[0].url)
							elif msg.embeds and msg.embeds[0].image.url:
								auth = ""
								for b in msg.embeds[0].to_dict()["fields"]:
									if "Sender" in b["name"]:
										auth = b["value"]
								await self.__buildEmbed(msg, msg.embeds[0].image.url, msg.embeds[0].description, auth)
							else:
								await self.__buildEmbed(msg, '')
	
	@commands.group()
	@perms.mod()
	async def starboard(self, ctx):
		"""Generic container for embed commands. run <p>help starboard for more info."""
		return

	@starboard.command()
	@perms.mod()
	async def delentry(self, ctx, msglink: str):
		"""Removes the given message from the archive cache."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
			return

		msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
		"""
		msg_data[0] -> server id
		msg_data[1] -> channel id
		msg_data[2] -> msg id
		"""
		try:
			self.arrs(str(msg_data[1])+str(msg_data[2]), msg_data[0], False)
		except:
			await ctx.send("Failed to remove from database")
			return
		await ctx.send("Removed.")

	@starboard.command()
	@perms.mod()
	async def override(self, ctx, msglink: str, link: str):
		"""Overrides the image that was going to the archived originally."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
			return

		msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
		"""
		msg_data[0] -> server id
		msg_data[1] -> channel id
		msg_data[2] -> msg id
		"""

		if self.s.find_one(server_id=ctx.message.guild.id) is not None:
			self.exceptions.append(msg_data[1] + msg_data[2])

	@starboard.command()
	@perms.mod()
	async def channelamount(self, ctx, amount:int, channel: discord.TextChannel = None):
		"""Change the amount of emotes needed for a specific channel. If no channel is passed, it adjusts for the current channel."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		else:
			if channel == None:
				channel = ctx.message.channel
			if self.o.find_one(channel_id=channel.id):
				self.o.update(dict(channel_am=amount), [channel.id])
			else:
				self.o.insert(dict(channel_id=channel.id, channel_am=amount))

	@starboard.command()
	@perms.mod()
	async def amount(self, ctx, b: int):
		"""Sets the amount of emotes required for a message to reach starboard."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		else:
			try:
				self.s.update(dict(archive_emote_amount=b, server_id=ctx.message.guild.id), ['server_id'])
			except:
				await ctx.send("Failed to change amount.")
				return
		await ctx.send("Succesfully changed amount to {}".format(b))

	@starboard.command()
	@perms.mod()
	async def emote(self, ctx, archive_emote: discord.Emoji):
		"""Sets the emote required for a message to reach starboard."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		else:
			try:
				self.s.update(dict(archive_emote=archive_emote.id, server_id=ctx.message.guild.id), ['server_id'])
			except:
				await ctx.send("Failed to change emote.")
				return
		await ctx.send("Succesfully changed emote to {}".format(archive_emote))

	@starboard.command()
	@perms.mod()	
	async def setup(self, ctx, archive_channel: discord.TextChannel, archive_emote: discord.Emoji, archive_emote_amount: int):
		"""Sets up the starboard channel, emote and amount."""
		if self.s.find_one(server_id=ctx.message.guild.id) is not None:
			return

		try:
			self.s.insert(dict(archive_channel=archive_channel.id, archive_emote=archive_emote.id, archive_emote_amount=archive_emote_amount, server_id=ctx.message.guild.id))
		except Exception as E:
			await ctx.send("Failed to setup starboard.")
			print(E)
			return
		await ctx.send("Succesfully setup starboard")

	@starboard.command()
	@commands.is_owner()
	async def twitter(self, ctx, bearer_token: str):
		"""Setup the twitter bearer for twitter support."""
		try:
			dbc.save("bot", "twitter", bearer_token)
			await ctx.send("Successfully set Twitter token!")
			return
		except:
			await ctx.send("Failed to set token.")
			return

def setup(bot):
	bot.add_cog(Starboard(bot))