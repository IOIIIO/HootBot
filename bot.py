try:
    import discord
    import traceback
    from discord.ext import commands
    import dataset
except:
    print("Failed to load a module. Make sure to start the bot using start.py")
    exit()

try:
    botToken = 'b'
except Exception as e:
    print("Failed to set token.")
    print("Reason: {}".format(e))
    exit()

bot = commands.Bot(command_prefix='#', description="HootBot, hooting your images to safety!")
extensions = []

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
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="$help for help"))
	print('Startup Complete')
	print('...')

bot.run(botToken, bot=True, reconnect=True)
