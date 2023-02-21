from discord.ext import commands
from src.log import log_command
import re
import datetime
import os
import asyncio

class Reminder(commands.Cog):
    """Commands for interacting with GPT-3."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_reminders())
        self.src_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.abspath(os.path.join(self.src_dir, '..'))
        self.data_folder = os.path.join(self.parent_dir, 'data')
        self.data_file = os.path.join(self.data_folder, 'reminders.csv')

    async def check_reminders(self):
        while not self.bot.is_closed():
            now = datetime.datetime.now()
            reminders = []
            keep_lines = []
            # read reminders from file and check if any are due
            with open(self.data_file, 'r') as f:
                for line in f:
                    user_id, reminder_time, message = line.strip().split(",")
                    reminder_time = datetime.datetime.fromisoformat(
                        reminder_time)
                    if reminder_time <= now:
                        reminders.append((int(user_id), message))
                    else:
                        keep_lines.append(line)

            # write reminders that are not due back to file
            with open(self.data_file, 'w') as f:
                f.writelines(keep_lines)

            # send due reminders to users
            for user_id, message in reminders:
                try:
                    user = await self.bot.fetch_user(user_id)
                    await user.send(message)
                except Exception as e:
                    print(f"Failed to send reminder to user {user_id}: {e}")

            # wait for 1 minute before checking again
            await asyncio.sleep(1)

    @commands.command()
    @log_command
    async def remindme(self, ctx, *users: commands.Greedy[commands.UserConverter], message: str):

        # Define the regular expression pattern
        pattern = r"(\d+d)?(\d+h)?(\d+m)?\s*(.*)"

        # Match the regular expression pattern with the message string
        match = re.match(pattern, message)

        # Extract the duration and activity from the matched groups
        duration_days = match.group(1)
        duration_hours = match.group(2)
        duration_minutes = match.group(3)
        activity = match.group(4)

        # Extract the integer values for the days, hours, and minutes
        days = int(duration_days[:-1]) if duration_days else 0
        hours = int(duration_hours[:-1]) if duration_hours else 0
        minutes = int(duration_minutes[:-1]) if duration_minutes else 0

        now = datetime.datetime.now()

        # Create a timedelta object with the extracted duration
        duration = datetime.timedelta(days=days, hours=hours, minutes=minutes)

        # Add the duration to the current datetime to get the new datetime
        new_datetime = now + duration

        try:
            if not os.path.exists(self.data_folder):
                print("Log folder not found. Creating a new folder...")
                os.mkdir(self.data_folder)
            if not os.path.exists(self.data_file):
                print("Log file not found. Creating a new file...")
                open(self.data_file, 'a+').close()

            for user in users:
                with open(self.data_file, 'a+') as f:
                    f.write(f"{user.id},{new_datetime},{activity}\n")
            await ctx.message.add_reaction("✅")

        except Exception as e:
            print("Error: ", e)
            await ctx.message.add_reaction("❌")
            return
