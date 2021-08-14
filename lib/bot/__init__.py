from attr import fields
from discord import Intents, colour
from discord import Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from asyncio import sleep

from discord.utils import get

from ..db import db

import os
from discord.ext.commands.errors import CommandNotFound
from dotenv import load_dotenv
from datetime import datetime

from glob import glob

PREFIX = "!"
OWNER_IDS = [284932365720223746]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)
        self.all_ready = False

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

        if (all([getattr(self, cog) for cog in COGS])):
            self.all_ready = True

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        self.use_dms = False
        self.rename_time = None

        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=PREFIX, 
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print(" Setup complete")

    def run(self, version):
        load_dotenv()
        self.VERSION = version
        self.TOKEN = os.environ['TOKEN']

        print("running setup...")
        self.setup()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def print_message(self):
        await self.notif_channel.send("I am a timed notification!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.notif_channel.send("Now online!")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass
        # elif hasattr(ctx, exc.original): 
        #     raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(868354555627331605)
            self.notif_channel = self.get_channel(875185822050189372)
            self.scheduler.start()

            await self.notif_channel.send("Now online!")

            # embed = Embed(title="Now online!", description="Assistant Bot is now online.", colour=0x00FF00, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another Field", "This field is next to the other one.", True),
            #           ("A non-inline field", "This field will appear on it's own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)  
            # embed.set_author(name="Assistant Bot", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is the footer!")
            # await self.notif_channel.send(embed=embed)

            while not self.cogs_ready.all_ready:
                await sleep(0.5)

            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    # My Helper Functions
    async def get_notif_channel(self, guild):
        channel = get(guild.text_channels, name=bot.notif_channel_name)
        if (channel is None):
            channel = await guild.create_text_channel(bot.notif_channel_name)
        return channel

    def on_off_str(self, isOn):
        if (isOn):
            return "ON"
        else:
            return "OFF"

    async def send_notification(self, ctx, notif_text):
        user_mention = ctx.message.author.mention
        if (self.use_dms):
            user = ctx.message.author
            await user.send(user_mention + " " + notif_text)
        else:
            await self.notif_channel.send(user_mention + " " + notif_text)

    def get_rename_time_delay(self):
        current_time = datetime.now()
        difference = current_time - self.rename_time
        seconds_in_day = 24 * 60 * 60
        result = divmod(seconds_in_day * difference.days + difference.seconds, 60)
        return result

bot = Bot()