try:
    import discord
    import traceback
    from discord.ext import commands
except:
    print("Failed to load a module. Make sure to start the bot using start.py")
    exit()

import cogs.support.db as dbc
import sys

try:
    #botToken = dbc.db['bot'].find_one(name="token")["value"]
    botToken = dbc.ret('bot', "token")
    #print(botToken)
except Exception as e:
    print("Failed to set token.")
    print("Reason: {}".format(e))
    exit()

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=dbc.ret('bot', 'prefix'), description="HootBot, hooting your images to safety!", intents=intents)
extensions = ['cogs.default', 'cogs.updater', 'cogs.schedule', 'cogs.JazUtils', 'cogs.errors', 'cogs.embed',
            'rogue.main', 'rogue.instagram', 'rogue.reddit', 'cogs.rules']

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
            
@bot.event
async def on_ready():
    print('Logged in as {}, {}'.format(bot.user.name, bot.user.id))
    if b := dbc.ret('bot', 'status') is not None:
        await bot.change_presence(activity=discord.Game(name=b))
    print('Startup Complete')
    print('...')

bot.run(botToken, bot=True, reconnect=True)
