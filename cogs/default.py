import discord
from discord.ext import commands
import cogs.support.db as dbc
import sys, os
from discord.ext.commands.cooldowns import BucketType
import cogs.support.perms as perms

class Default(commands.Cog, name="General Commands"):
	"""Generic commands to control the bot."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@perms.mod()
	async def say(self, ctx, *, repl: str):
		"""Repeats what you said, stripping out mentions."""
		length = len(ctx.command.qualified_name) + len(self.bot.command_prefix)
		message = ctx.message.clean_content[length:] # For some odd reason clean_content contains the command invocation too.
		try:
			await ctx.message.delete()
		except:
			pass
		await ctx.send(message)

	@commands.command()
	@commands.is_owner()
	async def presence(self, ctx, *, b: str):
		"""Adjusts the bot's presence status."""
		try:
			dbc.save('bot', 'status', b)
			await self.bot.change_presence(activity=discord.Game(name=b))
			await ctx.send("Sucessfully changed presence status.")
		except Exception as e:
			await ctx.send("Failed to change presence status.")
			print(e)

	@commands.command()
	@commands.is_owner()
	async def prefix(self, ctx, *, b: str):
		"""Adjusts the bot's global prefix."""
		try:
			dbc.save('bot', 'prefix', b)
			self.bot.command_prefix = b
			await ctx.send("Succesfully changed prefix to: \"{}\"".format(b))
		except Exception as e:
			await ctx.send("Failed to change prefix.")
			print(e)

	@commands.command()
	async def neofetch(self, ctx):
		"""Prints the specs of the machine we\'re running on. Linux/macOS hosts only."""
		if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
			dire = os.listdir("nf") 
			if len(dire) != 0: # Check if NF is installed.
				e = os.popen('nf/neofetch --stdout').read().split("\n",2)[2]
				embed = discord.Embed()
				embed.add_field(name="Neofetch", value=e)
				await ctx.send(embed=embed)
			else:
				await ctx.send("Installing Neofetch.")
				os.popen('git clone https://github.com/dylanaraps/neofetch.git nf')
				await ctx.send("Installed, run the command again.")
		else:
			await ctx.send("Command not supported on this platform.")

def setup(bot):
	bot.add_cog(Default(bot))