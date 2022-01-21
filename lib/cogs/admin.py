import time
import itertools

import discord.ext.commands
from apscheduler.triggers.cron import CronTrigger

from discord.ext import commands, tasks

from lib.utils.file_utils import get_server_prefixes, update_server_prefixes, get_backup_params, update_backup_params
from lib.utils.admin_utils import server_prefix_manager, backup_manager


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.auto_backup.start()
        print(f"Backups set to run every {get_backup_params()['frequency']} hours")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        prefixes = get_server_prefixes()
        prefixes[str(guild.id)] = 's1'
        update_server_prefixes(prefixes)

    @commands.Cog.listener()
    async def on_message(self, message):
        bot_id = self.client.user.id

        if message.guild:
            response = server_prefix_manager(str(message.guild.id), bot_id, message.content)
            if response:
                await message.channel.send(response, delete_after=5)
                await message.channel.delete(delay=5)


    @commands.has_permissions(manage_messages=True)
    @commands.command(name='changeprefix',
                      aliases=['prefix'],
                      brief='   Changes server prefix',
                      help=('Changes server prefix.\n'
                            '*Can only be called by sever administrators*'),
                      usage='<new prefix>'
                      )
    async def change_prefix(self, ctx):
        prefixes = get_server_prefixes()
        if not ctx.guild:
            await ctx.send(f"Guild prefixes can only be changed by a command sent in one of its text channels")
            return

        guild_id = str(ctx.guild.id)

        if len(ctx.message.content.split(' ')) > 1:
            oldprefix = prefixes[guild_id]
            prefixes[guild_id] = ctx.message.content.split(' ')[1]
            await ctx.send(f'Prefix changed from `{oldprefix}` to `{prefixes[guild_id]}`')

        elif len(ctx.message.content.split(' ')) == 1:
            await ctx.send(f'The prefix for this server is: `{prefixes[guild_id]}`')

        else:
            await ctx.send(f'Only power users can change the server prefix\nServer prefix unchanged: `{prefixes[guild_id]}`')

        update_server_prefixes(prefixes)


    @commands.is_owner()
    @commands.command(name='shutdown')
    async def shutdown_bot(self, ctx):
        """
        POWER USER ONLY
        """
        async with ctx.typing():
            await self.client.close()

        backup_manager(shutdown=True)


    @commands.is_owner()
    @commands.command(
        name='forcebackup'
    )
    async def force_backup(self, ctx):
        time0 = time.perf_counter()
        backup_manager(force=True)
        time1 = time.perf_counter()
        await ctx.send(f"Backup completed in {round(time1-time0, 3):0.3f} seconds")


    @commands.is_owner()
    @commands.command(
        name='backupfrequency',
        aliases=['backupfreq']
    )
    async def set_backup_frequency(self, ctx):
        backup_params = get_backup_params()
        if len(mes := ctx.message.content.split()) > 1:
            if mes[1].isnumeric():
                backup_params['frequency'] = int(mes[1])
                self.auto_backup.change_interval(backup_params['frequency'])
                update_backup_params(backup_params)
                await ctx.send(f"Backups have been changed to run every {backup_params['frequency']} hour{'s' * (backup_params['frequency'] != 1)}")
        else:
            await ctx.send(f"Backups are set to run every {backup_params['frequency']} hour{'s' * (backup_params['frequency'] != 1)}")


    @commands.is_owner()
    @commands.command(
        name='backuplifespan',
        aliases=['backuplife']
    )
    async def set_backup_lifespan(self, ctx):
        backup_params = get_backup_params()
        if len(mes := ctx.message.content.split()) > 1:
            if mes[1].isnumeric():
                backup_params['lifespan'] = int(mes[1])
                update_backup_params(backup_params)
                await ctx.send(f"Backups have been changed to delete after {backup_params['lifespan']} hour{'s' * (backup_params['lifespan'] != 1)}")
        else:
            await ctx.send(f"Backups are set to delete after {backup_params['lifespan']} hour{'s' * (backup_params['lifespan'] != 1)}")

    @commands.is_owner()
    @commands.command(
        name='reload'
    )
    async def reload_cog(self, ctx):
        cogs = {k: v for k, v in self.client.cogs.items()}
        cmds = [x.__cog_commands__ for x in cogs.values()]

        cog_names_lower = [{x.lower()} for x in cogs.keys()]
        cmd_names = [set([y.qualified_name.lower() for y in x]) for x in cmds]
        aliases = [set(itertools.chain.from_iterable([[z.lower() for z in y.aliases] for y in x])) for x in cmds]

        cog_to_reload = []

        for arg in ctx.message.content.lower().split():
            for cog, cmd, alias in zip(cog_names_lower, cmd_names, aliases):
                if arg in set.union(cog, cmd, alias):
                    cog_to_reload.append(list(cog)[0])

        cogs_reloaded = []

        for cog in cog_to_reload:
            try:
                self.client.reload_extension(f"lib.cogs.{cog.lower()}")
            except discord.ext.commands.errors.ExtensionNotLoaded:
                self.client.load_extension(f"lib.cogs.{cog}")
            cogs_reloaded.append(cog)
        await ctx.send(f"{', '.join(cogs_reloaded)} reloaded", delete_after=3)
        await ctx.message.delete(delay=3)


    @tasks.loop(hours=get_backup_params()['frequency'])
    async def auto_backup(self):
        backup_manager()


def setup(client):
    client.add_cog(Admin(client))

