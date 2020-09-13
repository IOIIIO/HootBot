import discord
from discord.ext import commands
import cogs.support.db as dbc
import sys, os

class Updater(commands.Cog, name="General Commands"):
	def __init__(self, bot):
		self.bot = bot

@commands.group(brief='Updates the bot to the latest commit and restarts if necessary.')
async def update(ctx):
	if ctx.invoked_subcommand is None:
		if await self.bot.is_owner(ctx.message.author):
			e = os.popen('git pull').read()
			if "Already up to date." in e:
				r = "Not restarting."
				c = 0xff0000
			else:
				r = "Restarting!"
				c = 0x00ff00
			embed=discord.Embed(title="HootBot Updater", color=c)
			embed.add_field(name=r, value="```e\n{}```".format(e), inline=False)
			await ctx.send(embed=embed)
			if c == 0x00ff00:
				await bot.logout()
				os.execl(sys.executable, sys.executable, * sys.argv)

@update.group(brief='Updates the bot to the latest commit, updates requirements and restarts.')
async def pip(ctx):
	if await self.bot.is_owner(ctx.message.author):
		e = os.popen('git pull').read()
		if "Already up to date." in e:
			r = "Not restarting."
			c = 0xff0000
			p = ""
		else:
			log = json.loads(os.popen('curl --data "text=$(pip3 install -r requirements.txt)" https://file.io').read())["link"]
			r = "Restarting!"
			c = 0x00ff00
			p = "[Click here for log!]({})".format(log)
		embed=discord.Embed(title="HootBot Updater", color=c)
		embed.add_field(name=r, value="```e\n{}```".format(e), inline=False)
		if p != "":
			embed.add_field(name="pip return:", value="{}".format(p), inline=False)
		await ctx.send(embed=embed)
		if c == 0x00ff00:
			await bot.logout()
			os.execl(sys.executable, sys.executable, * sys.argv)

@update.group(brief='Updates the bot to the latest commit, stashing any local changes and restarts.')
async def stash(ctx):
	if await self.bot.is_owner(ctx.message.author):
		e = os.popen('git pull').read()
		if "Already up to date." in e:
			r = "Not restarting."
			c = 0xff0000
			p = ""
		else:
			log = json.loads(os.popen('curl --data "text=$(git stash)" https://file.io').read())["link"]
			e = os.popen('git pull').read()
			r = "Restarting!"
			c = 0x00ff00
			p = "[Click here for log!]({})".format(log)
		embed=discord.Embed(title="HootBot Updater", color=c)
		embed.add_field(name=r, value="```e\n{}```".format(e), inline=False)
		if p != "":
			embed.add_field(name="git stash return:", value="{}".format(p), inline=False)
		await ctx.send(embed=embed)
		if c == 0x00ff00:
			await bot.logout()
			os.execl(sys.executable, sys.executable, * sys.argv)

def setup(bot):
	bot.add_cog(Updater(bot))