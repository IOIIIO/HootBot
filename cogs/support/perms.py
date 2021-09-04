from discord.ext import commands

def mod():
    async def predicate(ctx):
        if not ctx.guild:
            raise commands.errors.NoPrivateMessage

        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)

        return (await ctx.bot.is_owner(ctx.author)) or getattr(permissions, "manage_messages")
    
    return commands.check(predicate)

def owner():
    return commands.is_owner()