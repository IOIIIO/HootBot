import discord
from discord.ext import commands
import time, datetime, json
import urllib.request

class Schedule(commands.Cog, name="Show Schedule Commands"):
	def __init__(self, bot):
		self.bot = bot
	async def showID(self, id):
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

	@commands.command(brief='Show when the next episode of the show will air.')
	async def schedule(self, ctx, *, id:str=None):
		tic = time.perf_counter()
		await ctx.channel.trigger_typing()
		try:
			if not id:
				temp = await self.showID("The Owl House")
			else:
				temp = await self.showID(id)
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

def setup(bot):
	bot.add_cog(Schedule(bot))