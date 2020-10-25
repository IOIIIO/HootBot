import json
import os
import re
import sys
from urllib.parse import parse_qs, urlparse, quote_plus
import urllib.request
import datetime
import time

def sr():
    start_reqs()

def start_reqs():
	print("")
	print("Failed to find one more more requirements, would you like to automatically install them?")
	print("(Requires pip3 to be installed on the system.)")
	x = input("Y/n: ")
	if str.lower(x) == "n":
		print("Bot can't start without requirements, have a nice day!")
		exit()
	else:
		os.system("pip3 install -r requirements.txt")

def sc():
	start_config()

def start_config():
	print("")
	print("Failed to find config file, would you like to create one?")
	x = input("Y/n: ")
	if str.lower(x) == "n":
		print("Boot can't start without config, have a nice day!")
		exit()
	else:
		print("")
		print("Bot Token:")
		id = input("> ")
		print("")
		print("Bot Owner ID:")
		id2 = input("> ")
		print("")
		print("prefix:")
		id3 = input("> ")
		temp = {"token" : id, "owner" : id2, "config": {"prefix" : id3}}
		json.dump(temp, open('bot.json', 'w'), indent=4)
		temp = 0
		id2 = 0
		id = 0

try:
	import discord
	from discord.ext import commands
	from bs4 import BeautifulSoup
	import requests
	from imgurpython import ImgurClient
	import praw
except:
	sr()

if os.path.isfile("bot.json"):
	cfg = json.load(open('bot.json'))
else:
	sc()
	cfg = json.load(open('bot.json'))


exceptions = []
try:
	reddit = praw.Reddit(client_id=cfg["config"]["reddit_id"],
                     client_secret=cfg["config"]["reddit_scr"],
                     refresh_token=cfg["config"]["reddit_tkn"],
                     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37")
except:
	pass

# https://stackoverflow.com/a/45579374
def get_id(url):
	u_pars = urlparse(url)
	quer_v = parse_qs(u_pars.query).get('v')
	if quer_v:
		return quer_v[0]
	pth = u_pars.path.split('/')
	if pth:
		return pth[-1]

"""
tweet is only used when we want to archive the text from a tweet or embed
"""
async def buildEmbed(msg, url, tweet = '', author = ''):
	if url != "":
		if cfg["config"]["cache"] == True:
			try:
				url2 = url
				if not any(ext in url for ext in ['.mp4', ".mov", ".webm", ".webp"]):
					client = ImgurClient(cfg["config"]["imgur_usr"], cfg["config"]["imgur_scr"])
					url = client.upload_from_url(url, anon=True)["link"]
			except:
				url = url2
				pass
			
	embed = discord.Embed()
	if len(tweet):
		embed.add_field(name='Tweet/Embed Content', value=tweet, inline=False)
	elif isinstance(msg, discord.Message) and len(msg.content):
		embed.add_field(name='Content', value=msg.content, inline=False)
	embed.add_field(name='Message Link', value='https://discordapp.com/channels/{}/{}/{}'.format(msg.guild.id, msg.channel.id, msg.id), inline=False)
	auth = msg.author.mention
	embed.add_field(name='Author', value=auth, inline=True)
	embed.add_field(name='Channel', value=msg.channel.mention, inline=True)
	embed.set_image(url=url)

	await bot.get_channel(cfg[str(msg.guild.id)]['bot']['archive_channel']).send(embed=embed)

bot = commands.Bot(command_prefix=cfg["config"]["prefix"], owner=cfg["owner"])

@bot.event
async def on_ready():
	print('Logged in as {}'.format(bot.user.name))
	if cfg["config"] and cfg["config"]["reddit_id"] and cfg["config"]["reddit_scr"] != "":
		print('Logged into Reddit as {}'.format(reddit.user.me()))
	
	if cfg["config"] and cfg["config"]["presence"] and cfg['config']["presence"] != "":
		await bot.change_presence(activity=discord.Game(name=cfg["config"]['presence']))

"""
I use on_raw_reaction_add instead of on_reaction_add, because on_reaction_add doesn't work with messages that were sent before the bot went online.
"""
@bot.event
async def on_raw_reaction_add(payload):
	msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

	if str(payload.channel_id)+str(payload.message_id) in cfg[str(msg.guild.id)]['ignore_list']:
		return

	for reaction in msg.reactions:
		if str(reaction) == cfg[str(msg.guild.id)]['bot']['archive_emote']:
			url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', msg.content)
			if url:
				if 'dcinside.com' in url[0][0] and not msg.attachments:
					await bot.get_channel(payload.channel_id).send('https://discordapp.com/channels/{}/{}/{} not supported, please attach the image that you want to archive to the link.'.format(msg.guild.id, msg.channel.id, msg.id))

					cfg[str(msg.guild.id)]['ignore_list'].append(str(payload.channel_id)+str(payload.message_id))
					json.dump(cfg, open('bot.json', 'w'), indent=4)
					return
			if reaction.count >= cfg[str(msg.guild.id)]['bot']['archive_emote_amount']:
				if str(payload.channel_id)+str(payload.message_id) in exceptions:
					await buildEmbed(msg, exceptions[str(payload.channel_id)+str(payload.message_id)])

					exceptions.remove(str(payload.channel_id)+str(payload.message_id))
					json.dump(cfg, open('bot.json', 'w'), indent=4)
				else:
					cfg[str(msg.guild.id)]['ignore_list'].append(str(payload.channel_id)+str(payload.message_id))
					json.dump(cfg, open('bot.json', 'w'), indent=4)
					
					if url:
						if msg.attachments:
							await buildEmbed(msg, msg.attachments[0].url)
						else:
							processed_url = requests.get(url[0][0].replace('mobile.', '')).text
							"""
							most sites that can host images, put the main image into the og:image property, so we get the links to the images from there
							<meta property="og:image" content="link" />
							"""
							if 'deviantart.com' in url[0][0] or 'www.instagram.com' in url[0][0] or 'tumblr.com' in url[0][0] or 'pixiv.net' in url[0][0]:
								await buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'))
							elif 'twitter.com' in url[0][0]:
								"""
								either archive the image in the tweet if there is one or archive the text
								"""
								res = json.loads(requests.get('https://api.twitter.com/1.1/statuses/lookup.json?id={}&tweet_mode=extended'.format(re.findall(r'.*?twitter\.com\/.*?\/status\/(\d*).*?', url[0][0])[0]), headers={"Authorization": "Bearer {}".format(cfg["config"]["twitter"])}).text)
								if 'user' in res[0]:
									if 'media' in res[0]['entities']:
										await buildEmbed(msg, res[0]["entities"]["media"][0]["media_url"])
									else:
										await buildEmbed(msg, "", res[0]["full_text"])
								else:
									print(res)
							elif 'youtube.com' in url[0][0] or 'youtu.be' in url[0][0]:
								await buildEmbed(msg, 'https://img.youtube.com/vi/{}/0.jpg'.format(get_id(url[0][0])))
							elif 'dcinside.com' in url[0][0]:
								await buildEmbed(msg, msg.attachments[0].url)
							elif 'imgur' in url[0][0]:
								if 'i.imgur' not in url[0][0]:
									await buildEmbed(msg, BeautifulSoup(processed_url, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content').replace('?fb', ''))
								else:
									await buildEmbed(msg, url[0][0])
							elif 'https://tenor.com' in url[0][0]:
								for img in BeautifulSoup(processed_url, 'html.parser').findAll('img', attrs={'src': True}):
									if 'media1.tenor.com' in img.get('src'):
										await buildEmbed(msg, img.get('src'))
							elif "reddit.com" in url[0][0] or "redd.it" in url[0][0]:
								await buildEmbed(msg, return_reddit(url[0][0]))
							else:
								if msg.embeds and msg.embeds[0].url != url[0][0]:
									await buildEmbed(msg, msg.embeds[0].url, msg.embeds[0].fields[0].__getattribute__('value'))
								else:
									if msg.attachments:
										await buildEmbed(msg, msg.attachments[0].url)
									else:
										await buildEmbed(msg, '')
					else:
						if msg.attachments:
							await buildEmbed(msg, msg.attachments[0].url)
						elif msg.embeds and msg.embeds[0].image.url:
							auth = ""
							for b in msg.embeds[0].to_dict()["fields"]:
								if "Sender" in b["name"]:
									auth = b["value"]
							await buildEmbed(msg, msg.embeds[0].image.url, msg.embeds[0].description, auth)
						else:
							await buildEmbed(msg, '')

def return_reddit(url):
	api_url = '{}.json'.format(url)
	r = requests.get(api_url, headers = {'User-agent': 'Starboard v1.0'}).json()
	try:
		url = r[0]["data"]["children"][0]["data"]["media_metadata"]["u6yr7w5mstb51"]["s"]["u"].replace("&amp;", "&")
	except:
		url = r[0]["data"]["children"][0]["data"]["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
	#else:
	#	url = ""
	if ".jpg" in url:
		return url
	else:
		return ''

async def redembed(message):
	if cfg[str(message.guild.id)]['reddit'] == True:
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
				if url != []:
					url2 = re.sub(r'\?.*', "", url[0][0])
					if "reddit.com" in url2 or "redd.it" in url2:
						try:
							b = return_reddit(url2)
							if b != '':
								embed=discord.Embed(title="Reddit Embed", description=message.content)
								embed.add_field(name='Sender', value=message.author.mention)
								embed.set_image(url=b)
								await message.channel.send(embed=embed)
						except:
							pass

async def insta(message):
	if cfg[str(message.guild.id)]['insta'] == True:
				url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
				if url != []:
					if "instagram.com" in url[0][0]:
						embed=discord.Embed(title="Instagram Embed", description=message.content)
						embed.add_field(name='Sender', value=message.author.mention)
						embed.set_image(url=BeautifulSoup(requests.get(url[0][0].replace('mobile.', '')).text, 'html.parser').find('meta', attrs={'property':'og:image'}).get('content'))
						await message.channel.send(embed=embed)

@bot.event
async def on_message(message):
	if not isinstance(message.channel, discord.channel.DMChannel):
		if 'insta' in cfg[str(message.guild.id)]:
			await insta(message)

		if 'reddit' in cfg[str(message.guild.id)]:
			await redembed(message)

	await bot.process_commands(message)

def is_owner(ctx):
	if str(ctx.message.author.id) == cfg["owner"]:
		return True
	else:
		return False

"""
Used to setup the bot.
"""
@bot.command(brief='Sets up the bot.')
@commands.has_permissions(administrator=True)
async def setup(ctx, archive_channel: discord.TextChannel, archive_emote: discord.Emoji, archive_emote_amount: int):
	if str(ctx.guild.id) in cfg:
		return
	
	cfg[str(ctx.guild.id)] = {
		'ignore_list': [],
		'bot': {
			'archive_channel': archive_channel.id,
        	'archive_emote': str(archive_emote),
        	'archive_emote_amount': archive_emote_amount,
		}
	}
	json.dump(cfg, open('bot.json', 'w'), indent=4)

@bot.command(help="Sets the amount of emotes required for a message to reach starboard.", brief='Change the emote amount requirement.')
@commands.has_permissions(administrator=True)
async def setamount(ctx, b: int):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Server not in config. Use setup command first.")
	else:
		cfg[str(ctx.guild.id)]["bot"]['archive_emote_amount'] = b
	await ctx.send("Succesfully changed amount to {}".format(b))
	json.dump(cfg, open('bot.json', 'w'), indent=4)

"""
Change default presence.
"""
@bot.command(brief='Sets the default presence.')
async def presence(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'presence' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await bot.change_presence(activity=discord.Game(name=b))

"""
Change default prefix.
"""
@bot.command(brief='Change the bot prefix.')
async def prefix(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'prefix' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		bot.command_prefix = b
		await ctx.send("Succesfully changed prefix to: \"{}\"".format(b))

"""
Toggle whether cache should be used.
"""
@bot.group(brief='Toggle whether cache should be used.')
async def cache(ctx):
	if ctx.invoked_subcommand is None:
		if is_owner(ctx):
			if "cache" in cfg["config"]:
				if cfg["config"]["cache"] == True:
					cfg["config"].update({'cache' : False})
					b = "disabled"
				else:
					cfg["config"].update({'cache' : True})
					b = "enabled"
			else:
				cfg["config"].update({'cache' : True})
				b = "enabled"
			json.dump(cfg, open('bot.json', 'w'), indent=4)
			await ctx.send("Succesfully changed cache state to: \"{}\"".format(b))

@cache.command(brief='Set imgur UserID.')
async def user(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'imgur_usr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@cache.command(brief='Set imgur Secret.')
async def secret(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'imgur_scr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@bot.command(brief='Set twitter bearer.')
async def twitter(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'twitter' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated bearer key.")
	b = 0
"""
Toggle automatic Instagram embeds.
"""

@bot.group(brief="Allow bot to embed images which are normally broken")
async def embed(ctx):
	pass

@embed.group(brief='Toggle automatic Instagram embeds.')
@commands.has_permissions(administrator=True)
async def instagram(ctx):
	if "insta" in cfg[str(ctx.message.guild.id)]:
		if cfg[str(ctx.message.guild.id)]["insta"] == True:
			cfg[str(ctx.message.guild.id)].update({'insta' : False})
			b = "disabled"
		else:
			cfg[str(ctx.message.guild.id)].update({'insta' : True})
			b = "enabled"
	else:
		cfg[str(ctx.message.guild.id)].update({'insta' : True})
		b = "enabled"
	json.dump(cfg, open('bot.json', 'w'), indent=4)
	await ctx.send("Succesfully changed embed state to: \"{}\"".format(b))

@embed.group(name="reddit", brief="Configure reddit embed settings")
async def redd(ctx):
	pass
	
@commands.has_permissions(administrator=True)
@redd.command(brief='Toggle automatic Reddit embeds.')
async def enable(ctx):
	if "reddit" in cfg[str(ctx.message.guild.id)]:
		if cfg[str(ctx.message.guild.id)]["reddit"] == True:
			cfg[str(ctx.message.guild.id)].update({'reddit' : False})
			b = "disabled"
		else:
			cfg[str(ctx.message.guild.id)].update({'reddit' : True})
			b = "enabled"
	else:
		cfg[str(ctx.message.guild.id)].update({'reddit' : True})
		b = "enabled"
	json.dump(cfg, open('bot.json', 'w'), indent=4)
	await ctx.send("Succesfully changed embed state to: \"{}\"".format(b))

@redd.command(brief='Set Reddit ID.')
async def id(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_id' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@redd.command(brief='Set Reddit Secret.')
async def secret(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_scr' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

@redd.command(brief='Set Reddit Token.')
async def token(ctx, *, b: str):
	if is_owner(ctx):
		cfg["config"].update({'reddit_tkn' : b})
		json.dump(cfg, open('bot.json', 'w'), indent=4)
		await ctx.send("Succesfully updated key.")
	b = 0

"""
Update the bot and restarts
"""
@bot.group(brief='Updates the bot to the latest commit and restarts if necessary.')
async def update(ctx):
	if ctx.invoked_subcommand is None:
		if is_owner(ctx):
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
	if is_owner(ctx):
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
	if is_owner(ctx):
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

"""
Print neofetch in chat
"""
@bot.command(brief='Prints the specs of the machine we\'re running on. Linux/macOS hosts only.')
@commands.has_permissions()
async def neofetch(ctx):
	if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
		if os.path.isfile("nf/neofetch"):
			e = os.popen('nf/neofetch --stdout').read().split("\n",2)[2];
			embed = discord.Embed()
			embed.add_field(name="Neofetch", value=e)
			await ctx.send(embed=embed)
		else:
			await ctx.send("Installing Neofetch.")
			os.popen('git clone https://github.com/dylanaraps/neofetch.git nf')
			await ctx.send("Installed, run the command again.")
	else:
		await ctx.send("Command not supported on this platform.")

"""
Show when the next episode of the show will air.
"""
def showID(id):
	"""
	Returns the list of the next episode to come in 0, pre-formatted date in 1 and if no new episode is present, returns the latest episode with 2 set to 1
	"""
	firstAPI = json.loads(urllib.request.urlopen("https://api.tvmaze.com/singlesearch/shows?q={}".format(quote_plus(id))).read().decode())
	showAPI = json.loads(urllib.request.urlopen("https://api.tvmaze.com/shows/{}/episodes".format(firstAPI["id"])).read().decode())
	b = None; c = None
	for a in reversed(showAPI):
		d = datetime.datetime.strptime(a['airstamp'].replace("+00:00", ""), "%Y-%m-%dT%H:%M:%S")
		if d > datetime.datetime.utcnow():
			b = a; c = d
		else:
			if b != None:
				return(b, c, 0, firstAPI)
			else:
				return(a, d, 1, firstAPI)

@bot.command(brief='Show when the next episode of the show will air.')
@commands.has_permissions()
async def schedule(ctx, *, id:str=None):
	tic = time.perf_counter()
	await ctx.channel.trigger_typing()
	try:
		if not id:
			temp = showID("The Owl House")
		else:
			temp = showID(id)
		if temp[2] != 1:
			embed=discord.Embed(title="New Episode Coming!", color=0x00FF00)
		else:
			embed=discord.Embed(title="No New Episode Found", description="Showing latest episode instead ", color=0xFF0000)
		embed.set_author(name="{} Schedule".format(temp[3]["name"]), url=temp[3]["url"])
		embed.add_field(name="Title:", value=temp[0]["name"], inline=False)
		embed.add_field(name="Release Date", value=temp[1].strftime('%d %b %Y UTC'), inline=True)
		embed.add_field(name="Release Time", value=temp[1].strftime('%H:%M UTC'), inline=True)
		embed.add_field(name="Link to Countdown", value=temp[1].strftime('[Click Here](https://www.timeanddate.com/countdown/generic?iso=%Y%m%dT%H%M&msg={}&csz=1)'.format(temp[0]['name'].replace(" ", "+"))), inline=False)
		embed.add_field(name="Link to Episode", value="[Click Here]({})".format(temp[0]["url"]), inline=True)
		toc = time.perf_counter()
		embed.set_footer(text="Generated in {} seconds.".format(round(toc-tic,2)))
		await ctx.send(embed=embed)
	except:
		await ctx.send("Couldn't reach API or find show. Try again later.")


"""
Deletes the given message from archive cache.
"""
@bot.command(brief='Removes the given message from the archive cache.')
@commands.has_permissions(administrator=True)
async def del_entry(ctx, msglink: str):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		return

	msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
	"""
	msg_data[0] -> server id
	msg_data[1] -> channel id
	msg_data[2] -> msg id
	"""

	cfg[ctx.guild.id]['ignore_list'].remove(str(msg_data[1])+str(msg_data[2]))
	json.dump(cfg, open('bot.json', 'w'), indent=4)


"""
Overrides the image that was going to the archived originally.
"""
@bot.command(brief='Overrides the image that was going to the archived originally.')
@commands.has_permissions(administrator=True)
async def override(ctx, msglink: str, link: str):
	if str(ctx.guild.id) not in cfg:
		await ctx.send("Please set up the bot with <>setup archive_channel archive_emote archive_emote_amount.")
		return
		
	msg_data = msglink.replace('https://canary.discordapp.com/channels/' if 'canary' in msglink else 'https://discordapp.com/channels/', '').split('/')
	"""
	msg_data[0] -> server id
	msg_data[1] -> channel id
	msg_data[2] -> msg id
	"""

	if msg_data[1] + msg_data[2] not in exceptions:
		exceptions.append(msg_data[1] + msg_data[2])

bot.run(cfg['token'])
