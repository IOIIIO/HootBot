import discord
from discord.ext import commands
import cogs.support.db as dbc
import requests

async def post(source, image):
		j = {
			"image": {
    			"description": "Uploaded from The Owl House Discord.",
    			"tag_input": "safe, starboard bot upload, add more tags!, s:the owl house, c:untagged",
    			"source_url": source
  			},
  			"url": image
		}
		r = requests.post("{}/api/v1/json/images?key={}".format(dbc.ret("bot", "archiveLink"), dbc.ret("bot", "archiveKey")), json=j)
		return r.json()


class Derpi(commands.Cog, name="Derpi Commands"):
	"""Commands related to archiving images to a Derpibooru."""
	def __init__(self, bot):
		self.bot = bot

	
	@commands.group()
	@commands.is_owner()
	async def archive(self, ctx):
		"""Toggles whether archive should be used."""
		if ctx.invoked_subcommand is None:
			if dbc.ret("bot", "archive") == None or False:
				b = True
			else:
				b = False
			dbc.save("bot", "archive", b)
			await ctx.send("Succesfully changed archive state to: \"{}\"".format(b))

	@archive.command()
	@commands.is_owner()
	async def key(self, ctx, *, b: str):
		"""Sets the Derpi key in the database."""
		dbc.save("bot", 'archiveKey', b)
		await ctx.send("Succesfully updated key.")
		b = 0
	
	@archive.command()
	@commands.is_owner()
	async def link(self, ctx, *, b: str):
		"""Sets the Derpi link in the database."""
		dbc.save("bot", 'archiveLink', b)
		await ctx.send("Succesfully updated key.")
		b = 0

def setup(bot):
	bot.add_cog(Derpi(bot))