import asyncio
import discord
import requests
import os
import io
from discord.ext import commands
from discord import ClientException
from music import Music
import datetime
from gpt import GPT3
from log import BrennerLog
import sys 


client = commands.Bot(command_prefix="?", intents=discord.Intents.all())
logger = BrennerLog.get_instance("logs/bot.log")

#############################    CLIENT EVENTS    #############################

# METHOD: on_ready()
# PURPOSE: executes once the client/bot has booted.
@client.event
async def on_ready():
    try:
        await client.add_cog(Music(client))
        await client.add_cog(GPT3(client))
        synced = await client.tree.sync()
        client.loop.create_task(status_task())    
        print("Synced: {}".format(synced))
    except ClientException:
        print("Failed to sync")
    

@client.tree.command()
async def longest_users(ctx: discord.Interaction, num_users: int = 5):
    # Get all members in the server
    members = sorted(ctx.guild.members, key=lambda x: x.joined_at)

    # Get the top 5 members who have been in the server for the longest
    longest_members = members[:num_users]

    # Prepare the message to be sent
    message = f"The top {num_users} users who have been in the server for the longest are:\n"
    for i, member in enumerate(longest_members, 1):
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        joined_at = member.joined_at.replace(tzinfo=datetime.timezone.utc)
        delta = now - joined_at
        message += f"{i}. {member.name} ({delta.days} days)\n" #\n

    # Send the message
    await ctx.response.send_message(message, ephemeral=True)


#  METHOD: status_task()
# PURPOSE: Is called on a loop from on_ready, and allows certain methods
#          to be asynchronously called during execution
async def status_task():
    while True:
        await asyncio.sleep(1)


#############################   CLIENT COMMANDS   #############################


#  METHOD: join
# PURPOSE: User can request that the bot joins the channel that they
#          are currently in. 
@client.command()
async def goto(ctx, message):
    """Moves the bot to a given channel ID"""
    try: 
        voiceChannel=ctx.guild.get_channel(int(message))  
        if ctx.voice_client is None:
            await voiceChannel.connect()
        else:
            await ctx.voice_client.move_to(voiceChannel)
    except ClientException:
        print(colors.FAIL + "Client Exception thrown in join()")


@client.command()
async def ping(ctx):
    # Get the latency of the bot
    latency = client.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


'''@client.command() # removed until I can make this safer
async def deleteMe(ctx):
    """Deletes every messages sent by the calling user in the channel"""
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == id):
            await message.delete()'''


@client.command()
async def cleanBot(ctx):
    """Deletes every message sent by the bot in the calling channel."""
    logger.log_command(ctx.author.id, 'hello')
    app_info = await client.application_info()
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == app_info.id):
            await message.delete()


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

client.help_command = commands.DefaultHelpCommand()
client.run(os.environ["DISCORD_TOKEN"])
