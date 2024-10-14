import json
import random

import discord
import numpy as np
from discord.ext import commands
from discord import app_commands

from typing import Optional, Union, Literal
from lib.utils.file_utils import bot_data, update_bot_data


# def get_bot_data():
#     with open('./data/bot_data.json', 'r') as f:
#         bot_data = json.load(f)
#     return bot_data

# def update_bot_data(new_bot_data):
#     with open('./data/bot_data.json', 'w') as fp:
#         json.dump(new_bot_data, fp, indent=4)


class Small_Cmds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.cogs_ready.ready_up('small_cmds')

    @app_commands.command(name='hello')
    @app_commands.guilds(824288433517232149)
    async def hello_slash(self, interaction: discord.Interaction, name: Optional[str] = None):
        if not name:
            await interaction.response.send_message(f"Hello <@{interaction.user.id}>")
        else:
            await interaction.response.send_message(f"Hello {name}")


    @app_commands.command(name='sex', description='sex')
    @app_commands.checks.cooldown(1, 300, key=lambda i: i.guild_id)
    @app_commands.checks.cooldown(1, 82800, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guilds(824288433517232149)
    async def sex_slash(self, interaction: discord.Interaction):

        sexlist = [
            '<:unless:836976813892436018>',
            '<:peepowtf:780599482508771348>',
            '<:peepowtf:780599482508771348>',
            '<:peepowtf:780599482508771348>',
            '<:cringe:833728005209456671>',
            '<:cringe:833728005209456671>',
            '<:cringe:833728005209456671>',
            '<:weirdge:831217712117448754>',
            '<:weirdge:831217712117448754>',
            '<:weirdge:831217712117448754>',
            '<a:blushge:828312281603113012>'
        ]
        await interaction.response.send_message(sexlist[int(random.random() * len(sexlist))])


    # @commands.cooldown(1, 300, commands.BucketType.user)
    # @commands.command(name='ex',
    #                   brief='   Sex',
    #                   help='Sex'
    #                   )
    # async def ex(self, ctx):
    #     sexlist = [
    #         '<:unless:836976813892436018>',
    #         '<:peepowtf:780599482508771348>',
    #         '<:peepowtf:780599482508771348>',
    #         '<:peepowtf:780599482508771348>',
    #         '<:cringe:833728005209456671>',
    #         '<:cringe:833728005209456671>',
    #         '<:cringe:833728005209456671>',
    #         '<:weirdge:831217712117448754>',
    #         '<:weirdge:831217712117448754>',
    #         '<:weirdge:831217712117448754>',
    #         '<a:blushge:828312281603113012>'
    #     ]
    #     await ctx.send(sexlist[int(random.random() * len(sexlist))])
    #
    # @commands.command(name='',
    #                   aliases=['heesh'],
    #                   brief='   sheeeeeeeeeesh',
    #                   help='sheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeesh <:sheesh:844934490635108362>',
    #                   usage='none'
    #                   )
    # async def sheesh(self, ctx):
    #     await ctx.send(f"sh{'e' * int(random.random() * 28 + 2)}sh")
    #     await ctx.send('<:sheesh:844934490635108362>')

    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command(name='heesh',
                      brief='   sheeeeeeeeeesh',
                      help='sheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeesh <:sheesh:844934490635108362>',
                      usage='none'
                      )
    async def sheesh(self, ctx: discord.ext.commands.Context):
        # bot_data = get_bot_data()
        await ctx.message.delete(delay=0.1)
        if ctx.guild.id == 780376195182493707 and ctx.channel.id != 1089587184987811961:
            await ctx.send("Use in the thread, idot", delete_after=2)
            return
        try:
            channel = ctx.channel.id
        except:
            channel = 1
        pb = False
        wr = False
        bot_channel = channel in [780393312695746580]
        try:
            old_wr = bot_data['sheesh_leaderboard'][list(bot_data['sheesh_leaderboard'])[0]]
        except:
            old_wr = 0

        normal = int(abs(np.random.normal(2, 15, 1)[0]))
        if str(ctx.author.id) in bot_data['sheesh_leaderboard']:
            if normal + 2 > old_wr:
                wr = True
            elif normal + 2 > bot_data['sheesh_leaderboard'][str(ctx.author.id)]:
                pb = True

        else:
            bot_data['sheesh_leaderboard'][str(ctx.author.id)] = normal + 2
            bot_data['sheesh_leaderboard'] = {k: v for k, v in sorted(bot_data['sheesh_leaderboard'].items(), key=lambda item: item[1], reverse=True)}
            print(f"New user score: {normal + 2} ({ctx.author.id})")
            update_bot_data()

        await ctx.send(f"{ctx.author.mention} sh{'e' * (normal + 2)}sh _({normal + 2})_" +
                       (f"\n**NEW Personal Best!**\n_Previous was {bot_data['sheesh_leaderboard'][str(ctx.author.id)]}_" if pb and not wr and not bot_channel else '') +
                       (f"\n**NEW World Record!**\n_Previous was {old_wr}_" if wr and not bot_channel else ''))
        await ctx.send('<:sheesh:844934490635108362>')

        if pb or wr:
            bot_data['sheesh_leaderboard'][str(ctx.author.id)] = normal + 2
            bot_data['sheesh_leaderboard'] = {k: v for k, v in sorted(bot_data['sheesh_leaderboard'].items(), key=lambda item: item[1], reverse=True)}
            update_bot_data()
            print(('Personal ' if pb else '') + f'High Score Updated ({ctx.author.id})')

    @commands.command(name='heeshleaderboard',
                      aliases=['heesh-leaderboard', 'heeshlb', 'slb'],
                      brief='   sheeeeeeeeeesh',
                      help='sheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeesh <:sheesh:844934490635108362>',
                      usage='none'
                      )
    async def sheesh_leaderboard(self, ctx):

        # bot_data = get_bot_data()

        message = ctx.message.content

        arrs = [[], [], []]
        tie = 0
        place = 1
        prev_user = list(bot_data['sheesh_leaderboard'])[0]

        for user, amnt in bot_data['sheesh_leaderboard'].items():
            if amnt != bot_data['sheesh_leaderboard'][prev_user]:
                place += tie
                if tie:
                    tie = 1
                # else:
                #     place += 1
            else:
                tie += 1
            arrs[0].append(f"{place}")
            arrs[1].append(f"<@{user}>")
            arrs[2].append(f"{amnt}")

            prev_user = user

        top_x = 10
        for x in message.split():
            if x.isnumeric():
                top_x = int(x) if int(x) < 25 else (25 if len(arrs[0]) > 25 else len(arrs[0]))

        embed = discord.Embed(
            title='Sheesh Leaderboard <:sheesh:844934490635108362>'
        )

        embed.add_field(
            name='Rank',
            value='\n'.join(arrs[0][:top_x])
        )
        embed.add_field(
            name='User',
            value='\n'.join(arrs[1][:top_x])
        )
        embed.add_field(
            name='Length',
            value='\n'.join(arrs[2][:top_x])
        )

        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Small_Cmds(client))
