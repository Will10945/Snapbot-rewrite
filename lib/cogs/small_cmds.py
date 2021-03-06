import random

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option


class Small_Cmds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="hello",
        description="Sends hello",
        # options=[
        #     create_option(
        #         name="ping",
        #         description="Pings user back if true",
        #         required=False,
        #         option_type=3,
        #         choices=[
        #             create_choice(
        #                 name="True",
        #                 value="Hello asdasd"
        #             ),
        #             create_choice(
        #                 name="False",
        #                 value="Hello"
        #             )
        #         ]
        #     )
        # ]
    )
    async def _hello(self, ctx: SlashContext, option: str):
        await ctx.send(option)

    @commands.command(name='hello',
                      aliases=['hi'],
                      brief='   Says hello',
                      help=('Pings the user and says hello. \n'
                            'Used to check if the bot is online')
                      )
    async def hello(self, ctx):
        await ctx.send(f"Hello <@{ctx.author.id}>")


    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(name='ex',
                      brief='   Sex',
                      help='Sex'
                      )
    async def ex(self, ctx):
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
        await ctx.send(sexlist[int(random.random() * len(sexlist))])

    @commands.command(name='',
                      aliases=['heesh'],
                      brief='   sheeeeeeeeeesh',
                      help='sheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeesh <:sheesh:844934490635108362>',
                      usage='none'
                      )
    async def sheesh(self, ctx):
        await ctx.send(f"sh{'e' * int(random.random() * 28 + 2)}sh")
        await ctx.send('<:sheesh:844934490635108362>')


def setup(client):
    client.add_cog(Small_Cmds(client))
