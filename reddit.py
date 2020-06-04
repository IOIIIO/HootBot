import discord
import json
from bs4 import BeautifulSoup
import requests
import re
from discord.ext import commands

# TODO: Replace this using a central settings management system
# HACK! This uses the same bot.json file as the main.py file, 
# potential file handle conflicts could occur.
cfg = json.load(open('bot.json'))

class reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def return_reddit(self, url):
        try:
            # Form an API URL, like https://www.reddit.com/r/TheOwlHouse/comments/gqf70w/my_art_luz_and_amity_when_quarantine_is_over_what/.json
            api_url = '{}.json'.format(url)
            r = requests.get(api_url, headers = {'User-agent': 'RogueStarboard v1.0'}).json()
            url = r[0]["data"]["children"][0]["data"]["url"]

            # TODO: video embeds don't work
            if not url.startswith("https://www.reddit.com/") and not url.startswith("https://v.redd.it/"):
                return r[0]["data"]["children"][0]["data"]["url"]
        except Exception as e:
            print(e)

    # Listener to find messages with a Reddit link and generate an embed
    @commands.Cog.listener()
    async def on_message(self, message):
        if cfg[str(message.guild.id)]['reddit'] == True:
            url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
            if url != []:
                # TODO: Follow redd.it link redirect to call embed code on resulting long link
                if "reddit.com" in url[0][0] or "redd.it" in url[0][0]:
                    try:
                        embed=discord.Embed(title="Reddit Embed", description=message.content)
                        embed.add_field(name='Sender', value=str(message.author))
                        b = self.return_reddit(url[0][0])
                        embed.set_image(url=b)
                        await message.channel.send(embed=embed)
                    except:
                        pass
    
    @commands.command(brief='Toggle automatic Reddit embeds.')
    @commands.has_permissions(administrator=True)
    async def embed_reddit(self, ctx):
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