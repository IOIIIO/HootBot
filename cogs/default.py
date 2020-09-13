import discord
from discord.ext import commands
import cogs.support.db as dbc
import sys, os
from discord.ext.commands.cooldowns import BucketType

class Default(commands.Cog, name="General Commands"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(brief='Sets the default presence.')
	@commands.is_owner()
	async def presence(self, ctx, *, b: str):
		try:
			dbc.save('bot', 'status', b)
			await self.bot.change_presence(activity=discord.Game(name=b))
			await ctx.send("Sucessfully changed presence status.")
		except Exception as e:
			await ctx.send("Failed to change presence status.")
			print(e)

	@commands.command(brief='Change the bot prefix.')
	@commands.is_owner()
	async def prefix(self, ctx, *, b: str):
		try:
			dbc.save('bot', 'prefix', b)
			self.bot.command_prefix = b
			await ctx.send("Succesfully changed prefix to: \"{}\"".format(b))
		except Exception as e:
			await ctx.send("Failed to change prefix.")
			print(e)

	@commands.command(brief='Prints the specs of the machine we\'re running on. Linux/macOS hosts only.')
	async def neofetch(self, ctx):
		if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
			if os.path.isfile("nf/neofetch"):
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

	@commands.command(brief='Add a moderator role specific to the current guild.')
	@commands.cooldown(1, 60, BucketType.guild)
	@commands.guild_only()
	async def modrole(self, ctx, role: discord.Role = None):
		if role != None:
			try:
				dbc.save(str(ctx.message.guild.id), 'mod_role', role.id)
			except:
				await ctx.send("Failed to change modrole.")
			await ctx.send("Successfully changed modrole to {}".format(role.name))
		else:
			try:
				dbc.save(str(ctx.message.guild.id), 'mod_role', None)
			except:
				await ctx.send("Failed to reset modrole")
			await ctx.send("Successfully reste modrole")

def setup(bot):
	bot.add_cog(Default(bot))