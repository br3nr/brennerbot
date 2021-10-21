import discord
import random
from discord.ext import commands
from collections import Counter

responses = [
                "Silence jabroni."
        ]

client = commands.Bot(command_prefix = "+")

async def initBully(message):
    uid = str(message.author.id)
    chance = random.randint(0, 100)
    if chance < 90:
        choice = random.randint(0,10)
        if choice > 2:
            response = random.choice(responses)
            await message.channel.send("<@"+uid+">" + response)
        elif choice <= 2:
            await message.author.send(random.choice(responses))
