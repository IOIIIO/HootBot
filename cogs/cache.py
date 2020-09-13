import discord
from discord.ext import commands
import cogs.support.db as dbc

class Cache(commands.Cog, name="General Commands"):
	def __init__(self, bot):
		self.bot = bot

	def __owner(self, ctx):
		return self.bot.is_owner(ctx.message.author)

    @commands.group(brief='Toggle whether cache should be used.')
	@commands.check(self.__owner())
	async def cache(self, ctx):
		if ctx.invoked_subcommand is None:
			if dbc.ret("bot", "cache") == None or False:
				b = True
			else:
				b = False
			dbc.save("bot", "cache", b)
			await ctx.send("Succesfully changed cache state to: \"{}\"".format(b))

    @cache.command(brief='Set imgur UserID.')
	@commands.check(self.__owner())
    async def user(self, ctx, *, b: str):
        dbc.save("bot", 'imgur_usr', b)
	    await ctx.send("Succesfully updated key.")
	    b = 0

    @cache.command(brief='Set imgur Secret.')
	@commands.check(self.__owner())
    async def secret(self, ctx, *, b: str):
        dbc.save("bot", 'imgur_scr', b)
		await ctx.send("Succesfully updated key.")
    	b = 0

def setup(bot):
	bot.add_cog(Cache(bot))