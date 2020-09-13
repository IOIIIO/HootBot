from discord.ext import commands

def mod():
    if not commands.is_owner():
        return commands.has_guild_permissions(manage_messages=True)
    else:
        return commands.is_owner()