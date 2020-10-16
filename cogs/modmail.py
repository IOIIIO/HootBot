import discord
from discord.ext import commands
import cogs.support.db as dbc 
import cogs.support.perms as checks
import asyncio
import traceback
import sys

class Mail(commands.Cog, name="ModMail Commands"):
	"""Comands for setting up and using ModMail."""
	def __init__(self, bot):
		self.bot = bot
		self.s = dbc.db["modMail"]
		if list(dbc.db["modMail"].all()) == []:	
			try:
				dbc.db.query('CREATE TABLE modMail (server_id, type, location, anonymous, enabled, ping);')
				dbc.db.query('CREATE TABLE modMailOpen (server_id, channel_id, user_id);')
				print("Successfully created modmail tables.")
			except:
				print("Failed. Perhaps modmail tables already exist?")

	def __makeEmbed(self, ctx, content, type=False):
		if type == False:
			b = ctx.message
		else:
			b = ctx
		embed=discord.Embed(title="ModMail from {}".format(b.author.display_name))
		embed.set_thumbnail(url=b.author.avatar_url)
		embed.add_field(name="Message:", value=content, inline=False)
		embed.set_footer(text="Sent by: {} (ID: {})".format(b.author.name, b.author.id))
		return embed

	@commands.Command
	@commands.dm_only()
	@commands.max_concurrency(1, commands.BucketType.member)
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

		async def interact3(self, ctx):
			await ctx.send("What is your message? \n (You have 10 minutes till timeout and maximum 2000 characters.)")
			try:
				answer = await self.bot.wait_for('message', check=check, timeout=600)
				b = await interact4(self, ctx, answer.clean_content)
				return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		async def interact4(self, ctx, content):
			await ctx.send("Is this message correct? (y/n)")
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=30)
				if answer.content == "y":
					return content
				elif answer.content == "n":
					b = await interact3(self, ctx)
					return b
				else:
					await ctx.send("Invalid value.")
					b = await interact4(self, ctx, content)
					return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		for guild in self.bot.guilds:
			if self.s.find_one(server_id=guild.id) is not None and self.s.find_one(server_id=guild.id)["enabled"] == True:
				if guild.get_member(ctx.author.id) is not None:
					matchedGuilds[guild.id] = guild.name
		for b in range(len(matchedGuilds)):
			response = response + "{}. {} \n".format(b, list(matchedGuilds.values())[b])
		selectedGuild = await interact1(self, ctx) 
		if selectedGuild == None:
			return
		if ctx.message.user.id in self.s.find(server_id=selectedGuild)["user_id"]:
			ctx.send("You already have a session ongoing!")
			return
		await ctx.send("Okay, confirmed guild is: {} with ID {}".format(matchedGuilds[selectedGuild], selectedGuild))
		message = await interact3(self, ctx)
		if message == None:
			return
		embed = self.__makeEmbed(ctx, message)
		cttype = self.s.find_one(server_id=selectedGuild)["type"]
		if cttype == 1 or cttype == 2:
			try: 
				await self.bot.get_channel(int(self.s.find_one(server_id=selectedGuild)['location'])).send(embed=embed)
				await ctx.send("Sent")
			except:
				await ctx.send("Failed to send.")
		if cttype == 3:
			await ctx.send("This guild has two-way communication enabled. Moderators will be able to communicate with you through this DM. \n To end this conversation please type {}end. \n Attempting to establish communication.".format(ctx.prefix))
			try:
				channel = await self.bot.get_channel(self.s.find_one(server_id=selectedGuild)['location']).create_text_channel(name=ctx.message.author.name)
				await channel.send(embed=embed)
				dbc.db["modChatOpen"].insert(server_id=selectedGuild, channel_id=channel.id, user_id=ctx.message.author.id, dm_id=ctx.message.channel.id)
				await ctx.send("Established.")
			except:
				await ctx.send("Something went wrong.")
				return

	@commands.Cog.listener()
	async def on_message(self, message):
		if type(self.bot.get_channel(message.channel_id)) == discord.abc.GuildChannel:
			if message.channel_id in dbc.db["modChatOpen"].find(server_id=message.server_id)["channel_id"]:
				#chan = self.bot.get_user(dbc.db["modChatOpen"].find_one(channel_id=message.channel_id)["user_id"]).dm_channel
				chan = self.bot.get_channel(dbc.db["modChatOpen"].find_one(channel_id=message.channel_id))
				chan.send(embed=self.__makeEmbed(self, message, message.clean_content, True))

	@commands.Command
	@checks.mod()
	async def setupmodchat(self, ctx, type: int, anonymous: str, location: int, mention: discord.User = None):
		"""Sets"""
		if self.s.find_one(server_id=ctx.message.guild.id) is not None:
			return

		if type > 0 and type < 4:
			try:
				self.s.insert(dict(type = type, anonymous = anonymous, location = location, server_id=ctx.message.guild.id, enabled = True, ping = mention	))
			except Exception as E:
				await ctx.send("Failed to setup modchat.")
				print(E)
				return
			await ctx.send("Succesfully setup and enabled modchat")

	@commands.Command
	@checks.mod()
	async def togglemodchat(self, ctx):
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodchat to setup modchat first!".format(ctx.prefix))
			return
		
		try:
			if self.s.find_one(server_id=ctx.message.guild.id)["enabled"] == True:
				self.s.update(dict(server_id=ctx.message.guild.id, enabled=False), ["server_id"])
				await ctx.send("Succesfully disabled ModChat")
			else:
				self.s.update(dict(server_id=ctx.message.guild.id, enabled=True), ["server_id"])
				await ctx.send("Succesfully enabled ModChat")
		except:
			await ctx.send("Failed to change value.")

def setup(bot):
	bot.add_cog(Mail(bot))