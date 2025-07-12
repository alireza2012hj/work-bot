# auto_workbot.py
import discord
import asyncio
import os
import re
from datetime import datetime
import aiohttp

TOKEN = os.environ["TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
CHANNEL_ID = 1393495814004805704
RUN_DURATION = 15 * 60 * 60  # 15 hours

money_regex = re.compile(r"You .*? get .*?>(\d+)[\.\s]*")  # Parses money from -work result

class WorkBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        self.bg_task = self.loop.create_task(self.work_loop())
        self.shutdown_task = self.loop.create_task(self.auto_shutdown())

    async def work_loop(self):
        await self.wait_until_ready()
        self.channel = self.get_channel(CHANNEL_ID)

        if not isinstance(self.channel, discord.TextChannel):
            print("❌ Provided channel is not a TextChannel. Check the ID.")
            return

        self.total_earned = 0
        self.last_work_msg_id = None

        while not self.is_closed():
            try:
                await self.channel.send("-work")
                print("📤 Sent -work")
                await asyncio.sleep(3)

                # Fetch latest messages (fix: no .flatten())
                async for msg in self.channel.history(limit=5):
                    if msg.author.bot and msg.embeds:
                        embed = msg.embeds[0]
                        desc = embed.description or ""
                        match = money_regex.search(desc)
                        if match:
                            amount = int(match.group(1))
                            self.total_earned += amount
                            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                            await self.send_webhook_log(amount, timestamp, desc)
                            break

                await asyncio.sleep(1)
                await self.channel.send("-dep all")
                print("📤 Sent -dep all")
                await asyncio.sleep(120)  # Wait 2 minutes
            except Exception as e:
                print(f"⚠️ Error in loop: {e}")
                await asyncio.sleep(10)

    async def send_webhook_log(self, amount, timestamp, description):
        embed = {
            "title": "💼 Work Log",
            "description": f"{description}",
            "fields": [
                {"name": "Amount Earned", "value": f"`{amount}`", "inline": True},
                {"name": "Time", "value": f"`{timestamp}`", "inline": True}
            ],
            "color": 0x00ff00
        }
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_URL, json={"embeds": [embed]})

    async def auto_shutdown(self):
        await asyncio.sleep(RUN_DURATION)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        await self.send_shutdown_log(timestamp)
        print("⏱️ 15 hours reached. Shutting down.")
        await self.close()
        os._exit(1)

    async def send_shutdown_log(self, timestamp):
        embed = {
            "title": "🛑 Bot Shutdown",
            "description": "Bot automatically shut down after 15 hours.",
            "fields": [
                {"name": "Total Money Earned", "value": f"`{self.total_earned}`"},
                {"name": "Time", "value": f"`{timestamp}`"}
            ],
            "color": 0xff0000
        }
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_URL, json={"embeds": [embed]})

client = WorkBot(self_bot=True)
client.run(TOKEN)
