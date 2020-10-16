import discord
from discord.ext import commands
import cogs.support.db as dbc 
import cogs.support.perms as checks
import asyncio

class Mail(commands.Cog, name="ModMail Commands"):
	"""Comands for setting up and using ModMail."""
	def __init__(self, bot):
		self.bot = bot
		if dbc.db["modMail"] is None:	
			try:
				dbc.db.query('CREATE TABLE modMail (server_id,type,location,anonymous,enabled,);')
				print("Successfully created modmail tables.")
			except:
				print("Failed. Perhaps modmail tables already exist?")

	def __makeEmbed(self, bot, msg):
		embed=discord.Embed(title="ModMail from {}".format(msg.author.dislay_name))
		embed.set_thumbnail(url=msg.author.avatar_url)
		embed.add_field(name="Message:", value=msg.clean_content, inline=False)
		embed.set_footer(text="Sent by: {} (ID: {})".format(msg.author.name, msg.author.id))
		return embed

	@commands.Command
	@commands.dm_only()
	async def contact(self, ctx):
		await ctx.trigger_typing()
		matchedGuilds = {}
		response = ""

		def check(m):
			return m.author == ctx.message.author
		
		def checkBool(m):
			return m.author == ctx.message.author and (m.content == "y" or m.content == "n")

		async def interact1(self, ctx):
			await ctx.send(response + "Which server would you like to contact?")
			try:
				answer = await self.bot.wait_for('message', check=check, timeout=15)
				if answer.content.isdigit() and int(answer.content) < len(matchedGuilds):
					electedGuild = list(matchedGuilds.keys())[int(answer.content)]
					b = await interact2(self, ctx, electedGuild)
					return b
				else:
					await ctx.send("Invalid value.")
					b = await interact1(self, ctx)
					return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		async def interact2(self, ctx, electedGuild):
			await ctx.send("You chose server {} with ID {} \n Is this correct? (y/n)".format(matchedGuilds[electedGuild], electedGuild))
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=15)
				if answer.content == "y":
					return electedGuild
				elif answer.content == "n":
					b = await interact1(self, ctx)
					return b
				else:
					await ctx.send("Invalid value.")
					b = await interact2(self, ctx, electedGuild)
					return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		for guild in self.bot.guilds:
			if guild.get_member(ctx.author.id) is not None:
				matchedGuilds[guild.id] = guild.name
		for b in range(len(matchedGuilds)):
			response = response + "{}. {} \n".format(b, list(matchedGuilds.values())[b])
		selectedGuild = await interact1(self, ctx) 
		await ctx.send("Okay, confirmed guild is: {} with ID {}".format(matchedGuilds[selectedGuild], selectedGuild))

		

def setup(bot):
	bot.add_cog(Mail(bot))