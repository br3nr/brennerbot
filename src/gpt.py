import discord
from discord.ext import commands
from discord import app_commands
import openai
import requests
import io
import os
from src.log import log_command


class GPT3(commands.Cog):
    """Commands for interacting with GPT-3."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model_engine = "text-davinci-002"
        openai.api_key = os.environ["OPENAI_API_KEY"]

    @commands.command()
    async def chat(self, ctx, *, prompt):
        await ctx.send("I now use /chat instead of ?chat.")

    @app_commands.command(name="draw")
    @app_commands.describe(prompt="The descrption of image you want DALL·E to draw.")
    @log_command
    async def draw(self, interaction: discord.Interaction, prompt: str,):
        try:
            await interaction.response.defer()
            """Generates an image using DALL·E."""
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
            image_url = response['data'][0]['url']
            image_data = requests.get(image_url).content
            file = discord.File(io.BytesIO(image_data), "image.jpg")
            await interaction.followup.send(file=file)
        except openai.error.InvalidRequestError:
            await interaction.followup.send("Forbidden word in request")

    @app_commands.command(name="chat")
    @app_commands.describe(prompt="The prompt you want GPT-3 to respond to.")
    @app_commands.describe(temp="Creativity of response. Can be a float between 0.0 and 2.0")
    @log_command
    async def slash_chat(self, interaction: discord.Interaction, prompt: str, temp: float = 0.8) -> None:
        await interaction.response.defer()

        temp = min(temp, 2.0)
        prompt = prompt if prompt.endswith('?') else prompt + '.'

        model_engine = "text-davinci-002"
        completions = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=512,
            n=1,
            stop=None,
            temperature=temp,
        )
        message = completions.choices[0].text
        if len(message) > 2000:
            chunks = [message[i:i + 2000]
                      for i in range(0, len(message), 2000)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(message)

    @app_commands.command(name="chatgpt")
    @app_commands.describe(prompt="The prompt you want Chat GPT to respond to.")
    @log_command
    async def chatgpt(self, interaction: discord.Interaction, prompt: str,) -> None:

        await interaction.response.defer()

        messages = [
            {"role": "system", "content": "You are an helpful assistant."}
        ]

        message_str = {"role": "user", "content": prompt}
        messages.append(message_str)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages
        )

        reply = response['choices'][0]['message']['content']
        await interaction.followup.send(reply)
