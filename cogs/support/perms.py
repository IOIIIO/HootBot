from discord.ext import commands
import cogs.support.db as dbc

def mod():
    if not commands.is_owner():
        return commands.has_guild_permissions(manage_messages=True)
    else:
        return True