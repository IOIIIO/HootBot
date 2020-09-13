import discord
from discord.ext import commands
import cogs.support.db as dbc
import cogs.support.reddit as rdc
import sys, os, re, json
from bs4 import BeautifulSoup
import requests
from urllib.parse import parse_qs, urlparse, quote_plus
import cogs.support.db as dbc

class Starboard(commands.Cog, name="Starboard Commands"):
	def __init__(self, bot):
		self.bot = bot
		self.exceptions = []

	# https://stackoverflow.com/a/45579374
	def __get_id(self, url):
		u_pars = urlparse(url)
		quer_v = parse_qs(u_pars.query).get('v')
		if quer_v:
			return quer_v[0]
		pth = u_pars.path.split('/')
		if pth:
			return pth[-1]

	async def __buildEmbed(self, msg, url, tweet = '', author = ''):
		#if url != "":
			#if cfg["config"]["cache"] == True:
			#	try:
			#		url2 = url
			#		if not any(ext in url for ext in ['.mp4', ".mov", ".webm", ".webp"]):
			#			client = ImgurClient(cfg["config"]["imgur_usr"], cfg["config"]["imgur_scr"])
			#			url = client.upload_from_url(url, anon=True)["link"]
			#	except:
			#		url = url2
			#		pass
		embed = discord.Embed()
		if len(tweet):
			embed.add_field(name='Tweet/Embed Content', value=tweet, inline=False)
		elif isinstance(msg, discord.Message) and len(msg.content):
			embed.add_field(name='Content', value=msg.content, inline=False)
		embed.add_field(name='Message Link', value='https://discordapp.com/channels/{}/{}/{}'.format(msg.guild.id, msg.channel.id, msg.id), inline=False)
		if len(author):
			auth = msg.guild.get_member_named(author).mention
		else:
			auth = msg.author.mention
		embed.add_field(name='Author', value=auth, inline=True)
		embed.add_field(name='Channel', value=msg.channel.mention, inline=True)
		embed.set_image(url=url)

		await self.bot.get_channel(dbc.ret(str(msg.guild.id), 'archive_channel')).send(embed=embed)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

		if str(payload.channel_id)+str(payload.message_id) in dbc.ret(str(msg.guild.id), 'ignore_list'):
			return

		for reaction in msg.reactions:
			if str(reaction) == dbc.ret(str(msg.guild.id), 'archive_emote'):
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', msg.content)
				if url:
					if 'dcinside.com' in url[0][0] and not msg.attachments:
						await self.bot.get_channel(payload.channel_id).send('https://discordapp.com/channels/{}/{}/{} not supported, please attach the image that you want to archive to the link.'.format(msg.guild.id, msg.channel.id, msg.id))

						dbc.append(str(msg.guild.id), 'ignore_list', str(payload.channel_id)+str(payload.message_id))
						return
				if reaction.count >= dbc.ret(str(msg.guild.id), 'archive_emote_amount'):
					if str(payload.channel_id)+str(payload.message_id) in self.exceptions:
						await self.__buildEmbed(msg, self.exceptions[str(payload.channel_id)+str(payload.message_id)])

						self.exceptions.remove(str(payload.channel_id)+str(payload.message_id))
					else:
						dbc.append([str(msg.guild.id), 'ignore_list'], str(payload.channel_id)+str(payload.message_id))
						if url:
							if msg.attachments:
								await self.__buildEmbed(msg, msg.attachments[0].url)
							else:
								processed_url = requests.get(url[0][0].replace('mobile.', '')).text
								"""
								most sites that can host images, put the main image into the og:image property, so we get the links to the images from there
								<meta property="og:image" content="link" />
								"""
								if 'deviantart.com' in url[0][0] or 'www.instagram.com' in url[0][0] or 'tumblr.com' in url[0][0] or 'pixiv.net' in url[0][0]:
									await self.__buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'))
								elif 'twitter.com' in url[0][0]:
									"""
									either archive the image in the tweet if there is one or archive the text
									"""
									res = json.loads(requests.get('https://api.twitter.com/1.1/statuses/lookup.json?id={}&tweet_mode=extended'.format(re.findall(r'.*?twitter\.com\/.*?\/status\/(\d*).*?', url[0][0])[0]), headers={"Authorization": "Bearer {}".format(cfg["config"]["twitter"])}).text)
									if 'user' in res[0]:
										if 'media' in res[0]['entities']:
											await self.__buildEmbed(msg, res[0]["entities"]["media"][0]["media_url"])
										else:
											await self.__buildEmbed(msg, "", res[0]["full_text"])
									else:
										print(res)
								elif 'youtube.com' in url[0][0] or 'youtu.be' in url[0][0]:
									await self.__buildEmbed(msg, 'https://img.youtube.com/vi/{}/0.jpg'.format(self.__get_id(url[0][0])))
								elif 'dcinside.com' in url[0][0]:
									await self.__buildEmbed(msg, msg.attachments[0].url)
								elif 'imgur' in url[0][0]:
									if 'i.imgur' not in url[0][0]:
										await self.__buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content').replace('?fb', ''))
									else:
										await self.__buildEmbed(msg, url[0][0])
								elif 'https://tenor.com' in url[0][0]:
									for img in BeautifulSoup(processed_url, 'html.parser').findAll('img', attrs={'src': True}):
										if 'media1.tenor.com' in img.get('src'):
											await self.__buildEmbed(msg, img.get('src'))
								elif "reddit.com" in url[0][0] or "redd.it" in url[0][0]:
									await self.__buildEmbed(msg, rdc.return_reddit(url[0][0]))
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
	
	@commands.command(brief='Removes the given message from the archive cache.')
	@commands.has_guild_permissions(manage_messages=True)
	async def del_entry(self, ctx, msglink: str):
		if dbc.ret(str(ctx.message.guild.id), 'archive_channel') is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
			return

		msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
		"""
		msg_data[0] -> server id
		msg_data[1] -> channel id
		msg_data[2] -> msg id
		"""

		dbc.remove(str(ctx.guild.id), 'ignore_list', str(msg_data[1])+str(msg_data[2]))

	@commands.command(brief='Overrides the image that was going to the archived originally.')
	@commands.has_guild_permissions(manage_messages=True)
	async def override(self, ctx, msglink: str, link: str):
		if dbc.ret(str(ctx.message.guild.id), 'archive_channel') is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
			return

		msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
		"""
		msg_data[0] -> server id
		msg_data[1] -> channel id
		msg_data[2] -> msg id
		"""

		if msg_data[1] + msg_data[2] not in self.exceptions:
			self.exceptions.append(msg_data[1] + msg_data[2])

	@commands.command(help="Sets the amount of emotes required for a message to reach starboard.", brief='Change the emote amount requirement.')
	@commands.has_guild_permissions(manage_messages=True)
	async def setamount(self, ctx, b: int):
		if dbc.ret(str(ctx.message.guild.id), 'archive_channel') is None:
			await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		else:
			try:
				dbc.save(str(ctx.guild.id), 'archive_emote_amount', b)
			except:
				await ctx.send("Failed to change amount.")
				return
		await ctx.send("Succesfully changed amount to {}".format(b))

	@commands.command(brief='Sets up the bot.')
	@commands.has_guild_permissions(manage_messages=True)
	async def setup(self, ctx, archive_channel: discord.TextChannel, archive_emote: discord.Emoji, archive_emote_amount: int):
		if dbc.ret(str(ctx.message.guild.id), 'archive_channel') is None:
			return

		try:
			dbc.save(str(ctx.message.guild.id), 'ignore_list', [])
			dbc.save(str(ctx.message.guild.id), 'archive_channel', archive_channel.id)
			dbc.save(str(ctx.message.guild.id), 'archive_emote', archive_emote.id)
			dbc.save(str(ctx.message.guild.id), 'archive_emote_amount', archive_emote_amount)
		except:
			await self.bot.send("Failed to setup starboard.")
			return
		await self.bot.send("Succesfully setup starboard")


	@commands.command(brief='Set twitter bearer.')
	@commands.is_owner()
	async def twitter(self, ctx, *, b: str):
		dbc.ret('bot', 'twitter', b)
		await ctx.send("Succesfully updated bearer key.")
		b = 0


def setup(bot):
	bot.add_cog(Starboard(bot))