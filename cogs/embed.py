import discord
from discord.ext import commands
import cogs.support.db as dbc
import re
from bs4 import BeautifulSoup
import requests
import cogs.support.reddit as redcog
import cogs.support.perms as checks

class Embed(commands.Cog, name="Image Embedding Commands"):
	"""Comands for controlling the embedding of images that Discord normally doesn't."""
	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	@checks.mod()
	async def embed(self, ctx):
		"""Generic container for embed commands. run <p>help embed for more info."""
		return

	@embed.group()
	@checks.mod()
	async def instagram(self, ctx):
		"""Toggles whether Instagram images should be embedded"""
		if dbc.ret(str(ctx.message.guild.id), "insta") == None or False:
			b = True
		else:
			b = False
		dbc.save(str(ctx.message.guild.id), "insta", b)
		await ctx.send("Succesfully changed Instagram embed state to: \"{}\"".format(b))


	@embed.command()
	@checks.mod()
	async def reddit(self, ctx):
		"""Toggles whether Reddit images should be embedded."""
		if dbc.ret(str(ctx.message.guild.id), "reddit") == None or False:
			b = True
		else:
			b = False
		dbc.save(str(ctx.message.guild.id), "reddit", b)
		await ctx.send("Succesfully changed Reddit embed state to: \"{}\"".format(b))

	@commands.Cog.listener()
	async def on_message(self, message):
		if not isinstance(message.channel, discord.channel.DMChannel):
			if dbc.ret(str(message.guild.id), "insta") == True:
				await self.__instaembed(message)

			if dbc.ret(str(message.guild.id), "insta"):
				await self.__redembed(message)

		#await self.bot.process_commands(message)

	async def __redembed(self, message):
		url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
		if url != []:
			url2 = re.sub(r'\?.*', "", url[0][0])
			if "reddit.com" in url2 or "redd.it" in url2:
				try:
					b = redcog.return_reddit(url2)
					if b != '':
						embed=discord.Embed(title="Reddit Embed", description=message.content)
						embed.add_field(name='Sender', value=str(message.author))
						embed.set_image(url=b)
						await message.channel.send(embed=embed)
				except:
					pass

	async def __instaembed(self, message):
		url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
		if url != []:
			if "instagram.com" in url[0][0]:
				embed=discord.Embed(title="Instagram Embed", description=message.content)
				embed.add_field(name='Sender', value=str(message.author))
				embed.set_image(url=BeautifulSoup(requests.get(url[0][0].replace('mobile.', '')).text, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'))
				await message.channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Embed(bot))