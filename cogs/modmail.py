import discord
from discord.ext import commands
import cogs.support.db as dbc 
import cogs.support.perms as checks

class Mail(commands.Cog, name="ModMail Commands"):
	"""Comands for setting up and using ModMail."""
	def __init__(self, bot):
		self.bot = bot

    def __makeEmbed(self, bot, msg):
        

def setup(bot):
	bot.add_cog(Mail(bot))