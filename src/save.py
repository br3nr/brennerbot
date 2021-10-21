import discord
import os
import asyncio

async def save_me(ctx):
    file_name = (ctx.message.guild.name + "_" + ctx.message.channel.name + "_" +
                    ctx.message.author.name + "_" + ".txt")
    id = ctx.message.author.id
    file = open(file_name, "w")
    file.write(r" ____                                 ____        _   " + "\n" +
              r"| __ ) _ __ ___ _ __  _ __   ___ _ __| __ )  ___ | |_ " + "\n" +
              r"|  _ \| '__/ _ \ '_ \| '_ \ / _ \ '__|  _ \ / _ \| __|" + "\n" +
              r"| |_) | | |  __/ | | | | | |  __/ |  | |_) | (_) | |_ " + "\n" +
              r"|____/|_|  \___|_| |_|_| |_|\___|_|  |____/ \___/ \__|")


    async for message in ctx.channel.history(limit=None):
        if(message.author.id == id):
            file.write(message.content +"\n")

    with open(file_name, "rb") as file:
        await ctx.author.send("Here is your message history from the " + ctx.channel.name +
            " channel.", file=discord.File(file, file_name))
    os.remove(file_name)
    file.close()


async def writeMessage(message):
    if message.content.find("+") == -1:
        uid = str(message.author.id)
        file = "MessageBank\\" + uid
        messagefile = open(file, "a")
        messagefile.write(message.content + " \n")
        messagefile.close()
