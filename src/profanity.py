import discord
from discord.ext import commands
from collections import Counter

client = commands.Bot(command_prefix = "+")

blacklist = {"pearl jam", "nikon camera"}

async def scanForProfanity(message):
    words = []
    for i in blacklist:
        if message.content.lower().find(i) != -1:
            words.append(i)

    warningMessage = "Please do not say "
    pos = 0

    if(len(words) != 0):
        for i in words:
            warningMessage = warningMessage + i
            pos += 1
            if(pos < len(words)):
                warningMessage = warningMessage + " and/or "
        await message.channel.send(warningMessage, delete_after = 6)
