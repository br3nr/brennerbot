import discord
from discord.ext import commands
from discord import app_commands
from wavelink.ext import spotify
import openai
import os

class GPT3(commands.Cog):
    """Commands for interacting with GPT-3."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.model_engine = "text-davinci-002"
        self.api_key = os.environ["OPENAI_API_KEY"]

    @app_commands.command(name="chat")
    async def chat(self, interaction: discord.Interaction, prompt: str) -> None:
        """Responds to a promted using GPT-3."""
        # Replace "your_api_key_here" with your OpenAI API key
        openai.api_key = self.api_key
        completions = openai.Completion.create(
            engine=self.model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        message = completions.choices[0].text
        await interaction.response.send_message(message)