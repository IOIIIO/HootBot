import discord
from discord.ext import commands
import cogs.support.db as dbc
import re
from bs4 import BeautifulSoup
import requests
import cogs.support.reddit as redcog

class Embed(commands.Cog, name="Image Embedding Commands"):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(brief="Allow bot to embed images which are normally broken")
	async def embed(self, ctx):
	    pass

	@embed.group(brief='Toggle automatic Instagram embeds.')
	@commands.has_guild_permissions(manage_messages=True)
	async def instagram(self, ctx):
		if dbc.ret(str(ctx.message.guild.id), "insta") == None or False:
			b = True
		else:
			b = False
		dbc.save(str(ctx.message.guild.id), "insta", b)
		await ctx.send("Succesfully changed Instagram embed state to: \"{}\"".format(b))


	@embed.command(brief='Toggle automatic Reddit embeds.')
	@commands.has_guild_permissions(manage_messages=True)
	async def reddit(self, ctx):
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