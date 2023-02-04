import asyncio
import discord
import os
from discord.ext import commands
from discord import ClientException
from discord import app_commands
from src import save
from src import bullybot
from src.ui import ui
from music import Music
import datetime


client = commands.Bot(command_prefix="?", intents=discord.Intents.all())
u = ui()


#############################    CLIENT EVENTS    #############################




# METHOD: on_ready()
# PURPOSE: executes once the client/bot has booted.
@client.event
async def on_ready():
    try:
        await client.add_cog(Music(client))
        synced = await client.tree.sync()
        client.loop.create_task(status_task())    
        print("Synced: {}".format(synced))
        print("WELCOME")
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
    await ctx.response.send_message(message)


@client.tree.command(name="hello")
async def hello(ctx: discord.Interaction):
    await ctx.response.send_message(f"Hello {ctx.user.mention}!", ephemeral=True)


@client.tree.command(name="speak")
@app_commands.describe(arg="What should the bot say?")
async def speak(ctx: discord.Interaction, arg: str):
    await ctx.response.send_message(arg, ephemeral=True)

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
async def goto(ctx):
    try:
        guild = ctx.guild
        message = ctx.message.content[6:]
        voiceChannel=ctx.guild.get_channel(int(message))  

        if ctx.voice_client is None:
            await voiceChannel.connect()
        else:
            await ctx.voice_client.move_to(voiceChannel)
    except ClientException:
        print(colors.FAIL + "Client Exception thrown in join()")


@client.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''

    # Get the latency of the bot
    latency = client.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


# ---------------------------
#       SPEACH LOGIC 
# ---------------------------




# METHOD: say
# PURPOSE: Given that the bot is inside a VC, it will speak outloud given
#          the string provided by the user
@client.command()
async def say(ctx):
    try:    
        message = ctx.message.content
        command = 'espeak -p 10 -s 140 -a 1000 -ven-us --stdout "' + message[5:] + '" > message'
        os.system(command)
        f = open("message", "r")
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio(f, executable="ffmpeg", pipe=True,
                stderr=None, before_options="-fflags discardcorrupt -guess_layout_max 0", options=None))
        f.close()
        print("Done")
    except AttributeError:
        print(colors.FAIL + "Not in a voice channel")


# ---------------------------
#      MESSAGE CONTROL 
# ---------------------------

#  METHOD: wordSleuth()
# PURPOSE: Given a word specified by the user, searches previous messages in that channel
#          and tallies them, returning the total to the user.
@client.command()
async def wordSleuth(ctx, sleuth):
    id = ctx.message.author.id
    counter = 0
    async for message in ctx.channel.history(limit=None):
        if sleuth.lower() in message.content.lower():
            if(message.author.id == id):
                counter = counter + message.content.count(sleuth)

    sleuthed = "You said the word " + sleuth + " " + str(counter) +" times."
    await printToChannel(ctx.message, sleuthed)




#  METHOD: deleteMe()
# PURPOSE: Deletes every messages sent by the calling user in the channel
#          that deleteMe() was called in.
@client.command()
async def deleteMe(ctx):
    id = ctx.message.author.id
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == id):
            await message.delete()


"""
#  METHOD: cleanBot()
# PURPOSE: Deletes every message sent by the bot in the calling channel.
@client.command()
async def cleanBot(ctx):
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == 748778849751400871):
            await message.delete()
"""

#  METHOD: deleteLast()
# PURPOSE: Similar to deleteMe(), but deletes <num> amount of users messages
#          and then stops. 
@client.command()
async def deleteLast(ctx, num):
    counter = 0
    id = ctx.message.author.id
    try:
        num = int(num) + 1
        if(num <= 100 and num > 0):
            async for message in ctx.channel.history(limit=num):
                if(message.author.id == id):
                    await message.delete()
        else:
            raise ValueError("Bad Int")

    except ValueError as ve:
        await printToChannelDelete(ctx.message, "You are an idiot.")

"""
#  METHOD: saveMe()
# PURPOSE: Calls the save_me method in the save.py class
@client.command()
async def saveMe(ctx):
    await save.save_me(ctx)

"""
#############################   BOT METHODS   #############################


#  METHOD: printToChannel
# PURPOSE: Yeah u now
async def printToChannel(message, text):
    await message.channel.send(text)


#  METHOD: printThenDelete
# PURPOSE: Send a message to a channel, delete after few secs
async def printThenDelete(message, text):
    await message.channel.send(text, delete_after = 3)

"""
#  METHOD:
# PURPOSE:
async def bully(message):
    target = "example_uuid"
    uid = message.author.id
    if (uid == target):
        await bullybot.initBully(message)
"""

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


client.run(os.environ["DISCORD_TOKEN"])

