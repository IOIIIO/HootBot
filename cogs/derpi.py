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
		try: 
			r = requests.post(dbc.ret("bot", "archiveLink") + "/api/v1/json/images?key=" + dbc.ret("bot", "archiveKey"), json=j)
			b = r.json()
		except: 
			b = None
		return b


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

	@archive.command()
	@commands.is_owner()	
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

def setup(bot):
	bot.add_cog(Derpi(bot))
