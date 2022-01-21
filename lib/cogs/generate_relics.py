import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED

from discord.ext import commands
import discord

from lib.utils.file_utils import get_gen_relic_filepaths, get_gen_relics, get_gen_relics_data, get_prime_access_list, new_gen_relics_data
from lib.utils.relic_gen.gen_relic_tools import gen_relics_parse, show_relics_parse, create_relic_embed, parse_refinement, calculate_averages, \
                                                get_era_images
from lib.utils.relic_gen import relicbuilderv2

primeaccess = {}


class Generated_Relics(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.command(name='',
                      aliases=['build', 'gen'],
                      brief='   Creates a fake set of unvault relics',
                      help=('**Creates relics based on the given parameters** \n'
                            'You can choose between duplicates(default) or junk parts to fill extra space.\n\n'
                            'Include frames to build relics for frames of your choosing\n\n'
                            'Use \"random\" to build relics for random frames (default 2)\n\n'
                            'Use \"fake\" to build relics from Guthixbot\'s \"--fakeunvault\" command \n'
                            '(Guthixbot message must be within the 5 most recent messages in the channel)'),
                      usage='<Frame Frame ...> <d/j>\n\"fake\" <d/j>\n\"random\" <number of frames> <d/j>'
                      )
    async def buildrelics(self, ctx):

        user_id = ctx.author.id
        guild_id = None
        if ctx.guild:
            guild_id = ctx.guild.id

        flags = gen_relics_parse(ctx.message.content)

        if len(flags['pa']) < 2:
            await ctx.send(f"Relic build currently only works for 2+ prime accesses. Please add more frames you would like to see.\n"
                           f"If you can't make up your mind, you can add a number after the frame and it will fill in random prime accesses.")
            return


        with ThreadPoolExecutor(max_workers=None) as executor:
            tasks = [executor.submit(relicbuilderv2.takeinput, flags['pa'], flags['dupe'])]
            for task in as_completed(tasks):
                if task.result():
                    rel_cnt = len(get_gen_relics())
                    await ctx.send(f"**{rel_cnt}** relics generated for `{', '.join(flags['pa'])}`:", file=discord.File(get_gen_relic_filepaths()['generated_relics']))

            gen_relics_data = get_gen_relics_data()
            gen_relics_data['frames'] = flags['pa']
            new_gen_relics_data(gen_relics_data)


    @commands.command(name='relic',
                      aliases=['relics'],
                      brief='Shows contents of a generated relic',
                      help='Shows contents of a generated relic. \nUse without parameters to receive DMs of all the generated relics.',
                      usage='<Relic>'
                      )
    async def relic(self, ctx):

        args = ctx.message.content.split()
        channel = ctx.channel
        user = ctx.author
        embed_list = None

        if len(args) == 1:
            relics = get_gen_relics()
            channel = await user.create_dm()
            pa = get_gen_relics_data()['frames']

            await channel.send(f"All relics for generated unvault for: `{', '.join(pa)}`")
            await asyncio.sleep(1)

        else:
            relics, _ = show_relics_parse(args)

        if relics:
            embed_list = create_relic_embed(relics)

        if embed_list:
            for embed in embed_list:
                await channel.send(embed=embed)
                if len(embed_list) > 4:
                    await asyncio.sleep(1)


    @commands.command(name='average',
                      aliases=['avg'],
                      brief='Plat averages for generated relics',
                      help='Shows platinum averages for any of the most recently generated relics. \ni/e/f/r stands for intact/exceptional/flawless/radiant respectively',
                      usage='<Relic> <i/e/f/r>'
                      )
    async def average(self, ctx):

        era_images = get_era_images()

        args = ctx.message.content.title().split()
        relics, args = show_relics_parse(args)
        if not relics:
            if len(args) <= 2:
                relics = list(get_gen_relics())[:len(x := get_gen_relics()) if len(get_gen_relics()) < 10 else 10]
            else:
                await ctx.send("No valid relics, make sure they are in the list of recently generated relics and are spelled correctly.\n"
                               "To check the most recent relics, type `s!relics` and the I will DM you a list")
                return

        refinement = parse_refinement(args)
        averages = calculate_averages(relics, refinement)

        for avg, rel in zip(averages, relics):
            avg_str = ' <:platinum:897799994382352405>\n'.join(str(int(round(x))) for x in avg)
            avg_str += ' <:platinum:897799994382352405>'
            avg_embed = discord.Embed(
                color=(discord.Color.dark_teal() if 'Lith' in rel else discord.Color.blue() if 'Meso' in rel
                      else discord.Color.red() if 'Neo' in rel else discord.Color.gold())
            )
            avg_embed.set_author(icon_url=era_images[rel.split()[0]], name=f"{rel} {refinement}")
            avg_embed.add_field(
                name='Style',
                value='\n'.join(['Solo', '1b1', '2b2', '3b3', '4b4'])
            )
            avg_embed.add_field(
                name='Average',
                value=avg_str
            )

            await ctx.send(embed=avg_embed)
            if len(relics) > 4:
                await asyncio.sleep(1)



def setup(client):
    client.add_cog(Generated_Relics(client))
