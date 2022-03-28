from email import message
import discord
from discord.ext import commands
import cogs.support.db as dbc
import cogs.support.perms as perms
import requests

class Rules(commands.Cog, name="Rule Embed Commands"):
	"""Commands to use when setting up a rules channel."""
	def __init__(self, bot):
		self.bot = bot

	def get_attachment(self, ctx, direct, type):
		if type == 1:
			type_str = "text/plain"
		elif type ==  2:
			type_str = "image"

		if len(ctx.message.attachments) > 0:
			for a in ctx.message.attachments:
				if type_str in a.content_type:
					return a.url
		
		if direct != None:
			return direct
		else:
			return "No url/message nor attachement found."

	@commands.group()
	@perms.mod()
	async def rules(self, ctx):
		"""Generic container for rules commands. run <p>help rules for more info."""
		return

	@rules.group()
	@perms.mod()
	async def cimage(self, ctx, channel: discord.TextChannel, url: str = None, red: int = 200, green: int = 100, blue: int = 38, ):
		"""Send embed with image."""
		
		link = self.get_attachment(ctx, url, 2)
		if link == "No url/message nor attachement found.":
			ctx.send(link)
			return

		embed = discord.Embed(color=discord.Colour.from_rgb(red, green, blue))
		embed.set_image(url=link)

		await channel.send(embed=embed)

	@rules.group()
	@perms.mod()
	async def image(self, ctx, url: str = None,red: int = 200, green: int = 100, blue: int = 38, ):
		"""Send embed with image."""

		link = self.get_attachment(ctx, url, 2)
		if link == "No url/message nor attachement found.":
			ctx.send(link)
			return
		
		embed = discord.Embed(color=discord.Colour.from_rgb(red, green, blue))
		embed.set_image(url=url)

		await ctx.send(embed=embed)

	@rules.group()
	@perms.mod()
	async def text(self, ctx, title: str = None, message: str = None,red: int = 200, green: int = 100, blue: int = 38):
		"""Send embed with text."""

		link = self.get_attachment(ctx, message, 1)
		if link == "No url/message nor attachement found.":
			ctx.send(link)
			return
		if message == None or message == "":
			response = requests.get(link)
			data = response.text
		else:
			data = message

		embed = discord.Embed(color=discord.Colour.from_rgb(red, green, blue))
		
		if title != None and title != "":
			embed.title = title

		embed.description = data

		await ctx.send(embed=embed)

	@rules.group()
	@perms.mod()
	async def ctext(self, ctx, channel: discord.TextChannel, title: str = None, message: str = None,red: int = 200, green: int = 100, blue: int = 38):
		"""Send embed with text."""

		link = self.get_attachment(ctx, message, 1)
		if link == "No url/message nor attachement found.":
			ctx.send(link)
			return
		if message == None or message == "":
			response = requests.get(link)
			data = response.text
		else:
			data = message

		embed = discord.Embed(color=discord.Colour.from_rgb(red, green, blue))
		
		if title != None and title != "":
			embed.title = title

		embed.description = data

		await channel.send(embed=embed)

def setup(bot):
	bot.add_cog(Rules(bot))
	