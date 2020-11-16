import discord
from discord.ext import commands
import cogs.support.db as dbc 
import cogs.support.perms as checks
import asyncio
import re

class Mail(commands.Cog, name="ModMail Commands"):
	"""Comands for setting up and using ModMail."""
	def __init__(self, bot):
		self.bot = bot
		self.s = dbc.db["modMail"]
		if list(dbc.db["modMail"].all()) == []:	
			try:
				dbc.db.query('CREATE TABLE modMail (server_id, type, location, anonymous, enabled, ping);')
				dbc.db.query('CREATE TABLE modMailOpen (server_id, channel_id, user_id, dm_id);')
				print("Successfully created modmail tables.")
			except:
				print("Failed. Perhaps modmail tables already exist?")

	def __makeEmbed(self, ctx, content=None, type=False, anon=False):
		# Build embed with modmail message
		# content = string to be entered in Message field
		# type = specify if ctx is a ctx callback or message callback
		# anon = specify whether embed should be anonymous
		if type == False:
			b = ctx.message
			con = content
		else:
			b = ctx
			con = ctx.clean_content

		if con == None or con ==  "":
			con = 'None'

		if anon == False:
			dn = b.author.display_name
			pfp = b.author.avatar_url
			n = b.author.name
			i = b.author.id
		else:
			dn = "Anon"
			pfp = b.author.default_avatar_url
			n = "Anonymous"
			i = "-"
		
		embed=discord.Embed(title="ModMail from {}".format(dn))
		embed.set_thumbnail(url=pfp)
		embed.add_field(name="Message:", value=con, inline=False)
		if len(b.attachments) != 0:
			embed.set_image(url=b.attachments[0].url)
		embed.set_footer(text="Sent by: {} (ID: {})".format(n, i))
		return embed

	@commands.command()
	@commands.dm_only()
	@commands.max_concurrency(1, commands.BucketType.member)
	async def contact(self, ctx):
		"""Send a modmail to any configured server"""
		await ctx.trigger_typing()
		if dbc.db["modMailOpen"].find_one(user_id=ctx.message.author.id, dm_id=ctx.message.channel.id) is not None:
			ctx.send("Already in a conversation")
			return
		matchedGuilds = {}
		response = ""
		self.rec = 0; self.rec2 = 0

		def check(m):
			return m.author == ctx.message.author
		
		def checkBool(m):
			return m.author == ctx.message.author and (m.content == "y" or m.content == "n")

		async def interact1(self, ctx):
			try:
				self.rec = self.rec + 1
				if self.rec == 5:
					await ctx.send('Sorry, you took too long to answer.')
					return
			except NameError:
				self.rec = 0
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
			try:
				self.rec = self.rec + 1
				if self.rec == 5:
					await ctx.send('Sorry, you took too long to answer.')
					return
			except NameError:
				self.rec = 0
			await ctx.send("You chose server {} with ID {} \n Is this correct? (y/n)".format(matchedGuilds[electedGuild], electedGuild))
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=15)
				if answer.content.lower() == "y":
					return electedGuild
				elif answer.content.lower() == "n":
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
			nonlocal rec2
			print(rec2)
			self.rec2 = self.rec2 + 1
			if self.rec2 == 5:
				await ctx.send('Sorry, you took too long to answer.')
				return
			await ctx.send("What is your message? \n (You have 10 minutes till timeout and maximum 2000 characters.)")
			try:
				answer = await self.bot.wait_for('message', check=check, timeout=600)
				b = await interact4(self, ctx, answer.clean_content)
				return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		async def interact4(self, ctx, content):
			nonlocal rec2
			if rec2 == 0:
				rec2 = 0
			print(rec2)
			self.rec2 = self.rec2 + 1
			if self.rec2 == 5:
				await ctx.send('Sorry, you took too long to answer.')
				return
			await ctx.send("Is this message correct? (y/n)")
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=30)
				if answer.content.lower() == "y":
					return content
				elif answer.content.lower() == "n":
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
			if self.s.find_one(server_id=guild.id) is not None and self.s.find_one(server_id=guild.id)["enabled"] == True: # Get list of all servers with modmail enabled
				if guild.get_member(ctx.author.id) is not None: # Check which are shared with the user
					matchedGuilds[guild.id] = guild.name # And append them to the list
		for b in range(len(matchedGuilds)):
			response = response + "{}. {} \n".format(b, list(matchedGuilds.values())[b]) # Format list for picker
		if len(matchedGuilds) == 0: # No need to show the picker if no servers are shared
			await ctx.send("You don't share any servers with the bot that have modmail enabled.")
		elif len(matchedGuilds) == 1: # No need to show picker if just one server is shared
			selectedGuild = list(matchedGuilds.keys())[0]
		else:
			selectedGuild = await interact1(self, ctx) 
		if selectedGuild == None:
			return
		if ctx.message.author.id in self.s.find(server_id=selectedGuild):
			await ctx.send("You already have a session ongoing!")
			return
		await ctx.send("Okay, confirmed guild is: {} with ID {}".format(matchedGuilds[selectedGuild], selectedGuild))
		message = await interact3(self, ctx)
		if message == None:
			return
		
		cttype = self.s.find_one(server_id=selectedGuild)["type"]
		tag = None
		if self.s.find_one(server_id=selectedGuild)["ping"] is not None: # Check if server has a ping set up
			tag = self.s.find_one(server_id=selectedGuild)["ping"]
		else:
			tag = ""
		if cttype == 1 or cttype == 2:
			if self.s.find_one(server_id=selectedGuild)["anonymous"]:
				embed = self.__makeEmbed(ctx, message, anon=True)
			else:
				embed = self.__makeEmbed(ctx, message)
			try: 
				await self.bot.get_channel(int(self.s.find_one(server_id=selectedGuild)['location'])).send(embed=embed, content=tag)
				await ctx.send("Sent")
			except:
				await ctx.send("Failed to send.")
		if cttype == 3:
			embed = self.__makeEmbed(ctx, message)
			await ctx.send("This guild has two-way communication enabled. Moderators will be able to communicate with you through this DM. \n To end this conversation please type {}end. \n Attempting to establish communication.".format(ctx.prefix))
			try:
				channel = await self.bot.get_channel(self.s.find_one(server_id=selectedGuild)['location']).create_text_channel(name=ctx.message.author.id)
				await channel.send(embed=embed, content=tag)
				dbc.db["modMailOpen"].insert(dict(server_id=selectedGuild, channel_id=channel.id, user_id=ctx.message.author.id, dm_id=ctx.message.channel.id))
				await ctx.send("Established.")
			except:
				await ctx.send("Something went wrong. Try Again.")
				return

	@commands.Cog.listener()
	async def on_message(self, message):
		# Check for new messages
		# message = new message that has been created
		if message.author.id == self.bot.user.id:
			return
		if message.channel.type == discord.ChannelType.text:
			for b in dbc.db["modMailOpen"].find(server_id=message.guild.id):
				if int(message.channel.id) == int(b["channel_id"]) and int(message.channel.name) == int(b["user_id"]):
					user = self.bot.get_user(int(message.channel.name))
					if user.dm_channel is not None:
						chan = user.dm_channel
					else:
						chan = await user.create_dm()
					await chan.send(embed=self.__makeEmbed(message, type=True))
		elif message.channel.type == discord.ChannelType.private:
			for b in dbc.db["modMailOpen"].find(dm_id=message.channel.id):
				if message.channel.id == b["dm_id"] and message.author.id == b["user_id"]:
					chan = self.bot.get_channel(int(b["channel_id"]))
					await chan.send(embed=self.__makeEmbed(message, type=True))

	@commands.group()
	@checks.mod()
	async def modmail(self, ctx):
		"""Generic container for modmail commands. run <p>help modmail for more info."""
		return

	@modmail.command()
	@checks.mod()
	async def setup(self, ctx, type: int, anonymous: str, location: int, mention: discord.User = None):
		"""Initial setup for modmail"""
		if self.s.find_one(server_id=ctx.message.guild.id) is not None:
			return

		if anonymous == "False":
			anonymous = False
		elif anonymous == "True":
			anonymous = True

		if type > 0 and type < 4:
			try:
				self.s.insert(dict(type = type, anonymous = anonymous, location = location, server_id=ctx.message.guild.id, enabled = True, ping = mention	))
			except Exception as E:
				await ctx.send("Failed to setup modmail.")
				print(E)
				return
			await ctx.send("Succesfully setup and enabled modmail")

	@modmail.command()
	@checks.mod()
	async def location(self, ctx, location: int):
		"""Set a modmail channel"""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodmail to setup modmail first!".format(ctx.prefix))
			return

		try:
			self.s.update(dict(server_id=ctx.message.guild.id, location=location), ["server_id"])
			await ctx.send("Succesfully set modmail location to {}".format(location))
		except:
			await ctx.send("Failed to change value.")

		

	@modmail.command()
	@checks.mod()
	async def toggle(self, ctx):
		"""Toggle whether modmail is enabled"""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodmail to setup modmail first!".format(ctx.prefix))
			return
		
		try:
			if self.s.find_one(server_id=ctx.message.guild.id)["enabled"] == True:
				self.s.update(dict(server_id=ctx.message.guild.id, enabled=False), ["server_id"])
				await ctx.send("Succesfully disabled modmail")
			else:
				self.s.update(dict(server_id=ctx.message.guild.id, enabled=True), ["server_id"])
				await ctx.send("Succesfully enabled modmail")
		except:
			await ctx.send("Failed to change value.")

	@modmail.command()
	@checks.mod()
	async def anonymous(self, ctx):
		"""Toggle whether modmail should be anonymous"""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodmail to setup modmail first!".format(ctx.prefix))
			return
		
		try:
			if self.s.find_one(server_id=ctx.message.guild.id)["anonymous"] == True:
				self.s.update(dict(server_id=ctx.message.guild.id, anonymous=False), ["server_id"])
				await ctx.send("Succesfully disabled anonymous mode for modmail")
			else:
				self.s.update(dict(server_id=ctx.message.guild.id, anonymous=True), ["server_id"])
				await ctx.send("Succesfully enabled anonymous mode for modmail")
		except:
			await ctx.send("Failed to change value.")
	
	@modmail.command()
	@checks.mod()
	async def mention(self, ctx, mention = None):
		"""Set which role/user to mention with the first modmail."""
		role = False
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodmail to setup modmail first!".format(ctx.prefix))
			return
		if mention != None:
			mention = int("".join(re.findall(r'\d+', mention)))
		if not (ctx.message.guild.get_role(mention) == None or ctx.message.guild.get_member(mention) == None) or mention == '':
			await ctx.send("Invalid argument")
			return
		elif mention == None:
			mention2 = None
		else: 
			if ctx.message.guild.get_role(mention) != None:
				role = True
				mention2 = ctx.message.guild.get_role(mention).mention
			if role == False and ctx.message.guild.get_member(mention) != None:
				mention2 = ctx.message.guild.get_member(mention).mention
	
		try:
			self.s.update(dict(server_id=ctx.message.guild.id, ping=mention2), ["server_id"])
			if mention == None:
				mention2 = "None"
			await ctx.send("Succesfully set modmail ping to {}".format(mention2))
		except:
			await ctx.send("Failed to change value.")

	@modmail.command()
	@checks.mod()
	async def type(self, ctx, type: int):
		"""Sets which type of modmail to use on this guild."""
		if self.s.find_one(server_id=ctx.message.guild.id) is None:
			await ctx.send("Use {}setupmodmail to setup modmail first!".format(ctx.prefix))
			return
		
		try:
			self.s.update(dict(server_id=ctx.message.guild.id, type=type), ["server_id"])
			await ctx.send("Succesfully set modmail type to {}".format(type))
		except:
			await ctx.send("Failed to change value.")

	@commands.command()
	@commands.dm_only()
	async def end(self, ctx):
		"""End an open modmail conversation"""
		if dbc.db["modMailOpen"].find_one(user_id=ctx.message.author.id, dm_id=ctx.message.channel.id) is None:
			await ctx.send("Not in modmail conversation!")
			return

		def checkBool(m):
			return m.author == ctx.message.author and (m.content == "y" or m.content == "n")

		async def interact1(self, ctx):
			await ctx.send("Are you sure you want to end the conversation? (y/n)")
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=30)
				if answer.content.lower() == "y":
					return True
				elif answer.content.lower() == "n":
					return False
				else:
					await ctx.send("Invalid value.")
					b = await interact1(self, ctx)
					return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		try:
			end = await interact1(self, ctx)
			if end == True:
				chan = self.bot.get_channel(dbc.db["modMailOpen"].find_one(user_id=ctx.message.author.id, dm_id=ctx.message.channel.id)["channel_id"])
				dbc.db["modMailOpen"].delete(user_id=ctx.message.author.id, dm_id=ctx.message.channel.id, channel_id=chan.id)
				await chan.edit(name="old-{}".format(chan.name))
				await ctx.send("Ended succesfully")
			else:
				await ctx.send("Okay.")
		except:
			await ctx.send("Failed to end conversation.")

	@commands.command()
	@checks.mod()
	async def endoverride(self, ctx):
		"""Forcefully end an open modmail conversation"""
		if dbc.db["modMailOpen"].find_one(user_id=int(ctx.message.channel.name), channel_id=ctx.message.channel.id) is None:
			await ctx.send("Not in modmail conversation!")
			return

		def checkBool(m):
			return m.author == ctx.message.author and (m.content == "y" or m.content == "n")

		async def interact1(self, ctx):
			await ctx.send("Are you sure you want to end the conversation? (y/n)")
			try:
				answer = await self.bot.wait_for('message', check=checkBool, timeout=30)
				if answer.content.lower() == "y":
					return True
				elif answer.content.lower() == "n":
					return False
				else:
					await ctx.send("Invalid value.")
					b = await interact1(self, ctx)
					return b
			except asyncio.TimeoutError:
				await ctx.send('Sorry, you took too long to answer.')
				return

		try:
			end = await interact1(self, ctx)
			if end == True:
				chan = self.bot.get_channel(dbc.db["modMailOpen"].find_one(user_id=int(ctx.message.channel.name), channel_id=ctx.message.channel.id)["channel_id"])
				dbc.db["modMailOpen"].delete(user_id=int(ctx.message.channel.name), channel_id=ctx.message.channel.id)
				await chan.edit(name="old-{}".format(chan.name))
				await ctx.send("Ended succesfully")
			else:
				await ctx.send("Okay.")
		except:
			await ctx.send("Failed to end conversation.")

def setup(bot):
	bot.add_cog(Mail(bot))