# bot.py

# if running on a new machine, the following packages needed to be installed
# - discord
# - nest_asyncio

import os
import nest_asyncio
import discord
from dotenv import load_dotenv
import sys

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
# intents.presences = True


nest_asyncio.apply()
client = discord.Client(intents=intents)


#nest_asyncio.apply()
# client = discord.Client()

channels = []

async def action_on_ready():
    
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    
    for chan in guild.channels:
        if ( chan.name == "shadow-realm" ):
            await chan.send("bot is back on!")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    #await action_on_ready()
    #nest_asyncio.run(action_on_ready())


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    
    await msg.channel.send(msg.author.nick +"\n"+ msg.content)
    
    if msg.content == 'goodbye teabot':
        await msg.channel.send("oh no, you said the magic word! I'm being shut down now")
        
    for chan in client.guilds[0].channels:
        if ( chan.name == "shadow-realm" ):
            await chan.send("bot is sleeping!")
        break

@client.event
async def on_reaction_add(rxn, user):
    print(user.nick)
    await rxn.message.channel.send(user.nick)

print('client.run() called')
client.run(TOKEN)
print('client.run() complete')



# <url> to supress preview