import discord
from discord.ext import commands
import cogs.support.db as dbc

class Cache(commands.Cog, name="Cache Commands"):
	"""Commands related to managing the caching of starboard images."""
	def __init__(self, bot):
		self.bot = bot

    @commands.group()
	@commands.is_owner()
	async def cache(self, ctx):
		"""Toggles whether cache should be used."""
		if ctx.invoked_subcommand is None:
			if dbc.ret("bot", "cache") == None or False:
				b = True
			else:
				b = False
			dbc.save("bot", "cache", b)
			await ctx.send("Succesfully changed cache state to: \"{}\"".format(b))

    @cache.command()
	@commands.is_owner()
    async def user(self, ctx, *, b: str):
		"""Sets the Imgur user ID in the database."""
        dbc.save("bot", 'imgur_usr', b)
	    await ctx.send("Succesfully updated key.")
	    b = 0

    @cache.command()
	@commands.is_owner()
    async def secret(self, ctx, *, b: str):
		"""Sets the Imgur user Secret in the database."""
        dbc.save("bot", 'imgur_scr', b)
		await ctx.send("Succesfully updated key.")
    	b = 0

def setup(bot):
	bot.add_cog(Cache(bot))