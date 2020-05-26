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

class insta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Listener to find messages with an Instagram link and generate an embed
    @commands.Cog.listener()
    async def on_message(self, message):
        if not isinstance(message.channel, discord.channel.DMChannel):
            # TODO: Make a central settings management file
            # Check if the Insta setting is in the bot config and feature is enabled
            if 'insta' in cfg[str(message.guild.id)] and cfg[str(message.guild.id)]['insta'] == True:
                # TODO: Make this into a nice helper function
                # TODO: Caching would help Instagram not block the bot and speed up operations
                # Attempt to find a URL
                url = re.findall(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', message.content)
                if url != [] and ("instagram.com" in url[0][0]):
                    # Start making an embed, we found an Instagram link
                    embed=discord.Embed(title="Instagram Embed", description=message.content)
                    embed.add_field(name='Sender', value=str(message.author))

                    # TODO: This is an ugly looking string
                    # Grab metadata from Instagram and return the embed image from headers
                    embed.set_image(url=
                        BeautifulSoup(requests.get(url[0][0].replace('mobile.', '')).text, 'html.parser') \
                            .find('meta', attrs={'property':'og:image'}).get('content')
                    )

                    await message.channel.send(embed=embed)
    
    # TODO: Replace this using a central settings management system
    @commands.command(brief='Toggles whether to embed Instagram links')
    @commands.has_permissions(administrator=True)
    async def embed_instagram(self, ctx):
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