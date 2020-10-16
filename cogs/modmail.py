import discord
from discord.ext import commands
import cogs.support.db as dbc 
import cogs.support.perms as checks

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
        

def setup(bot):
	bot.add_cog(Mail(bot))