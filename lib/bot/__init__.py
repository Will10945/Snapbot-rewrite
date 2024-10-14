import asyncio
import json
import os
from asyncio import sleep
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents, Forbidden, HTTPException
from discord.ext.commands import Bot as BotBase, BadArgument, MissingRequiredArgument, \
    CommandOnCooldown, MissingPermissions, MissingRole, CommandNotFound

from lib.utils.file_utils import get_server_prefixes

OWNER_IDS = [148706546308612096]
COGS = [path.split(os.sep)[-1][:-3] for path in glob(f".{os.sep}lib{os.sep}cogs{os.sep}*.py")]
IGNORE_EXCEPTIONS = (BadArgument, SyntaxError, MissingRequiredArgument)

async def command_prefix(client, message):
    prefixes = get_server_prefixes()
    if message.guild is None:
        return ''
    elif str(message.guild.id) in list(prefixes):
        return prefixes[str(message.guild.id)]
    else:
        return 's!'

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.stdout = None
        self.ready = False
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler()

        super().__init__(
            command_prefix=command_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            asyncio.run(self.load_extension(f"lib.cogs.{cog}"))
            print(f" {cog} cog loaded")

        print("Setup complete.")

    def run(self, version):
        self.VERSION = version

        print("Running setup.")
        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running bot.")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot connected.")

    async def on_disconnect(self):
        print("Bot disconnected.")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Sorry, there was an error in this command.")

        await self.stdout.send("An error occurred")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, CommandNotFound):
            pass
        elif isinstance(exc, CommandOnCooldown):
            try:
                await ctx.send(f"Command is currently on cooldown, try again after {exc.retry_after:0.0f} seconds.", delete_after=2)
                await ctx.message.delete(delay=2)
            except:
                await ctx.response.send_message("Command is currently on cooldown, try again later.", ethereal=True)
        elif isinstance(exc, MissingPermissions):
            await ctx.send("You lack the permissions to use this command here.", delete_after=2)
            await ctx.message.delete(delay=2)
        elif isinstance(exc, MissingRole):
            await ctx.send("You lack the role required to use this command here.", delete_after=2)
            await ctx.message.delete(delay=2)
        elif hasattr(exc, "original"):
            if isinstance(exc.original, SyntaxError):
                await ctx.send("Something is wrong with the syntax of that command.", delay=2)
            elif isinstance(exc, HTTPException):
                await ctx.send("Unable to send message.")
            elif isinstance(exc, Forbidden):
                await ctx.send("I do not have permission to do that.")
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            # self.stdout = self.get_channel(799486810585694240)
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot ready.")
        else:
            print("Bot reconnected.")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
tree = bot.tree
