# auto_workbot.py
import discord
import asyncio
import os

TOKEN = os.environ["TOKEN"]  # Or replace with "your_token_here"

CHANNEL_ID = 1392908236876808394  # Replace with your actual text channel ID

class WorkBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        self.bg_task = self.loop.create_task(self.work_loop())

    async def work_loop(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        # ✅ Only proceed if it's a TextChannel
        if not isinstance(channel, discord.TextChannel):
            print("❌ Provided channel is not a TextChannel. Check the ID.")
            return

        while not self.is_closed():
            try:
                await channel.send("-work")
                print("📤 Sent -work")
                await asyncio.sleep(1)
                await channel.send("-dep all")
                print("📤 Sent -dep all")
                await asyncio.sleep(120)  # Wait 2 minutes
            except Exception as e:
                print(f"⚠️ Error in loop: {e}")
                await asyncio.sleep(10)

# ✅ Required for Pyright and proper Discord operation


client = WorkBot(self_bot=True)
client.run(TOKEN)