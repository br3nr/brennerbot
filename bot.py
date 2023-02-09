import asyncio
import discord
import requests
import os
import io
from discord.ext import commands
from discord import ClientException
from discord import app_commands
from src import save
from src import bullybot
from src.ui import ui
from music import Music
import datetime
from gpt import GPT3
import openai 

client = commands.Bot(command_prefix="?", intents=discord.Intents.all())
u = ui()


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
    """Moves the bo"""
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
    # Get the latency of the bot
    latency = client.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)


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


@client.command()
async def deleteMe(ctx):
    """Deletes every messages sent by the calling user in the channel"""
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == id):
            await message.delete()


@client.command()
async def cleanBot(ctx):
    """Deletes every message sent by the bot in the calling channel."""
    async for message in ctx.channel.history(limit=None):
        if(message.author.id == 748778849751400871):
            await message.delete()


@client.command()
async def chat(ctx, *, prompt):
    """Chat with the bot using GPT-3"""
    model_engine = "text-davinci-002"
    openai.api_key = os.environ["OPENAI_API_KEY"]
    print("message:", prompt)
    # Replace "your_api_key_here" with your OpenAI API key
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    await ctx.send(message)

@client.command()
async def draw(ctx, *, prompt):
    """Generates an image using DALL-E."""
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    image_url = response['data'][0]['url']
    # Get the image and send it to Discord
    image_data = requests.get(image_url).content
    file = discord.File(io.BytesIO(image_data), "image.jpg")
    await ctx.send(file=file)


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
