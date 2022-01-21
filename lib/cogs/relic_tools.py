import asyncio
import threading
import re

import discord
from datetime import datetime, time, timedelta

from discord.ext import commands, tasks
from discord.ext.commands import has_permissions

from lib.utils.file_utils import get_rarest_relics
from lib.utils.relic_utils import update_relic_dbs, set_parse, find_relics_with_sets, get_shared_relics, flatten_dict, is_prime_junk, \
                                  parse_related_relics, ERA_IMAGES
from lib.utils.spreadsheet_utils import check_for_website_update, availability_parser, availability_manager, update_steamcharts_data, parse_vault_order, \
                                        find_vault_order, update_unvault_relics, find_unvault_sets, get_full_sheet, sort_relics, is_related, related_sorted_time

class Relic_Tools(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.auto_update_relic_spreadsheet.start().set_name('auto_update_relic_spreadsheet')
        self.auto_update_steamcharts_info.start().set_name('auto_update_steamcharts_info')

        # self.asd.start().set_name('cringe test code')



    @commands.Cog.listener()
    async def on_ready(self):

        while not get_full_sheet():
            await asyncio.sleep(1)
        self.update_unvault_relics_db.start()

        time_until_midnight = (datetime.combine(datetime.today(), time.min) + timedelta(days=1)).timestamp() - datetime.now().timestamp()
        print(f"Auto Update Relics DB job added and starting in: {time_until_midnight:0.1f}s")
        await asyncio.sleep(time_until_midnight)
        self.auto_update_relic_dbs.start()




    @has_permissions(manage_messages=True)
    @commands.command(name='urelicdb')
    async def force_update_relic_dbs(self, ctx):
        th = threading.Thread(target=update_relic_dbs)
        th.start()


    @commands.command(name='sharedrelics',
                      aliases=['shared'],
                      brief='Shows relics that share parts for given sets',
                      help='Shows relics that share parts for given sets.\nSpace separated parameters',
                      usage='<set ...>'
                      )
    async def shared_relics(self, ctx):

        args = ctx.message.content.title().split()

        sets = set_parse(args)
        relics = find_relics_with_sets(sets, exclusive=True)

        sets = [_set.split(' Prime')[0] for _set in sets]

        if relics:
            embed = discord.Embed(
                title='Shared Relics',
                description=f"Relics shared by the following sets:\n**{', '.join(sets)}**"
            )
            embed.add_field(name='Relics', value='\n'.join(relics), inline=True)
        else:
            embed = discord.Embed(
                title='Shared Relics',
                description=f"No relics shared by the following sets:\n**{', '.join(sets)}**"
            )
        await ctx.send(embed=embed)

    @commands.command(name='available',
                      aliases=['availability', 'av', 'farmable'],
                      brief='   Get relic availability',
                      help='Gets total relic availability\n',
                      usage='<relic>'
                      )
    async def relic_availability(self, ctx):

        relics = await availability_parser(ctx.message.content.title().split())
        if not relics:
            await ctx.send(f"No valid relics detected, make sure you are spelling them correctly")
            return

        av_embed = await availability_manager(relics)
        imgfile = discord.File('./data/plot_image.png', filename='plot_image.png')
        av_embed.set_image(url='attachment://plot_image.png')

        await ctx.send(embed=av_embed, file=imgfile)

    @commands.command(name='unvaults',
                      aliases=['lastseen', 'vaultdate', 'vaulted', 'unvault'],
                      brief='   Gets a list of frames by date last seen',
                      help=('Pings the user and says hello. \n'
                            'Used to check if the bot is online')
                      )
    async def get_vault_order(self, ctx):
        args = ctx.message.content.split()

        if len(args) > 1:
            sets = parse_vault_order(args)
            valid_unvaults = find_unvault_sets(sets)
            unv_embed = None

            if not valid_unvaults:
                await ctx.send(f"No valid frames as command parameters")
                return

            for frame in valid_unvaults:
                unv_embed = discord.Embed(
                    title=f"Unvaults with {frame}",
                    description=f"Total Unvaults: **{len(valid_unvaults[frame])}**"
                )
                for unv in valid_unvaults[frame]:
                    unv_embed.add_field(
                        name=f"{unv}",
                        value='\n'.join(valid_unvaults[frame][unv])
                    )

            await ctx.send(embed=unv_embed)

        else:
            ordered_unvaults, active = find_vault_order()

            print_str = ''
            for k, v in ordered_unvaults.items():
                k_date = datetime.strptime(k, '%b %d %Y')
                print_str += f"{k} *({(datetime.now() - k_date).days} Day{'s' if (datetime.now() - k_date).days != 1 else ''})* : {', '.join(v)}\n"

            k_date = active[list(active)[0]]
            print_str += f"*Currently Available ({(datetime.now() - k_date).days} Day{'s' if (datetime.now() - k_date).days != 1 else ''}) : {', '.join(list(active))}*\n"

            await ctx.send(print_str)

    @commands.command(name='shared',
                      aliases=['sharedrelics'],
                      brief='Shows all relics containing a part for each set',
                      help='Shows all relics containing a part for each set.',
                      usage='<Set ...>'
                      )
    async def shared_relics(self, ctx):

        sets = set_parse(ctx.message.content.title().split())
        sets = list(set(sets))
        junk = [s for s in sets if is_prime_junk(s)]
        sets = [s for s in sets if not is_prime_junk(s)]
        if len(sets) < 2:
            await ctx.send('Must include at least 2 non-junk prime sets')
            return
        else:
            sets += junk
        relics = sorted(get_shared_relics(sets), key=sort_relics)

        unv_relic_sets = find_unvault_sets([x.split(' Prime')[0] for x in sets])
        unv_relic_sets = flatten_dict(unv_relic_sets)
        unv_relic_sets = list(set(unv_relic_sets))

        unv_relics = [x for x in relics if x in unv_relic_sets]
        pa_relics = [x for x in relics if x not in unv_relics]

        if pa_relics or unv_relics:
            embed = discord.Embed(
                title=f"Shared relics for:",
                description=f"{', '.join([s.split(' Prime')[0] for s in sets])}"
            )

            if pa_relics:
                embed.add_field(
                    name='PA Relics:',
                    value='\n'.join(pa_relics),
                    inline=True
                    )
            if unv_relics:
                embed.add_field(
                    name='Unvault Relics:',
                    value='\n'.join(unv_relics),
                    inline=True
                )

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"No relics shared between **{', '.join([s.split(' Prime')[0] for s in sets])}**")

    @commands.command(name='relatedrelics',
                      aliases=['related', 'rel', 'whatelse', 'also', 'otherrelics', 'other'],
                      brief='   Get related relics',
                      help='Gets related relics\n\n'
                           'Saying \"links\" after the relic will show a string of links '
                           'with calculated prices that you can paste directly into chat.'
                           '\n\n**Usage Explanation:**\n'
                           '`Prime Sets` will filter out relics that do not have a part for the listed sets\n'
                           'Filtered sets default to \"meta\" sets, Using \"expanded\" will use a bigger list\n'
                           'Other sets can be added on top of the \"meta\" and \"expanded\" lists\n\n'
                           '*In order to edit these values, a number must immediately follow the keyword*\n'
                           '\"__unvault__\" only shows relics in the same unvault if applicable\n'
                           '\"__junk__\" limits amount of prime junk and forma in relics shown `default=0`\n'
                           '\"__return__\" sets the lower limit of the value of relics shown `default=10`\n'
                           '\"__initial__\" sets your starting price for relics `default=0`\n'
                           '\"__increment__\" determines price scaling `default=10`\n'
                           '\"__sort__\" lets you set the sort style, currently only 1 (`sets`)\n\n'
                           '**Auto-pricing works like this:**\n'
                           'Price = (`initial` price) + ((`average return` of the relic) / (`increment`))\n'
                           'Prices are grouped and posted at the end of the block or when the price changes\n\n'
                           '**Examples:**\n'
                           '`s!related meso n5 average 15`\n'
                           'Shows relics available with Meso N5 above 15p return with at least one meta part\n'
                           '`s!related neo s13 meta limbo junk 2`\n'
                           'Shows relics available with Neo S13 with 2+ meta(+ limbo) parts\n'
                           '`s!related neo a4 unvault links`\n'
                           'Shows relics from the Ash/Vauban unvault and lists them as links with prices\n',
                      usage='_\* means optional_\n**<Relic>** \n\n\* \"return\" <value> \n\* \"initial\" <value> \n\* \"increment\" <value> \n\* \"junk\" <value> \n\* \"sort\" <value>\n\* <prime sets ...>\n\* \"links\"'
                      )
    async def related_relics(self, ctx):

        flags = parse_related_relics(ctx.author.id, ctx.message.content)

        if not flags['relics']:
            await ctx.send('You must provide at least one valid relic.')
            return

        relic_era = flags['relics'][0].lower().split()[0]

        if len(flags['relics']) > 1:
            related_dict = is_related(flags['relics'])

            embed = discord.Embed(
                title="Compared Availability Between:",
                description=', '.join(list(related_dict))
            )

            for relic in related_dict:
                value_str = ''
                for relic2 in related_dict[relic]['time_spans']:
                    days = related_dict[relic]['time_spans'][relic2]
                    value_str += f"{relic2}: {days} day{'s' if days != 1 else ''}\n"
                embed.add_field(
                    name=relic,
                    value=value_str,
                    inline=True
                )

            await ctx.send(embed=embed)

        elif flags['sort_style'] == 'Time':
            relics_sorted_time = related_sorted_time(flags)

            embed = discord.Embed(
                description=f"**Parameters:**\n"
                            f"Sort Style: `{flags['sort_style']}`\n"
                            f"Average Return: `{flags['average_return']}`\n"
                            f"Junk Amount: `{flags['junk_amount']}`\n"
                            f"Unvault Relics Only: `{flags['return_unvault']}`\n"
                            f"Rarest Relics Only: `{flags['rarest']}`\n"
                            f"Detailed: `{flags['detailed']}`\n\n"
                            f"For more info on parameters, check out `s!help related`",
                color=(discord.Color.teal() if 'lith' in relic_era.lower() else discord.Color.blue() if 'meso' in relic_era.lower()
                else discord.Color.red() if 'neo' in relic_era.lower() else discord.Color.gold())
            )
            embed.set_author(
                name=flags['relics'][0],
                icon_url=ERA_IMAGES[relic_era]
            )

            if flags['detailed']:
                for _time in relics_sorted_time:



                    for relic in relics_sorted_time[_time]:
                        pass

            else:
                time_sorted = {}
                for relic, span in relics_sorted_time['totals'].items():
                    if span not in time_sorted:
                        time_sorted[span] = []
                    time_sorted[span].append(relic)

                time_era_sorted = {}
                for _time, relic_list in time_sorted.items():
                    for relic in relic_list:
                        era = relic.split()[0]
                        name = relic.split()[1]
                        if _time not in time_era_sorted:
                            time_era_sorted[_time] = {}
                        if era not in time_era_sorted[_time]:
                            time_era_sorted[_time][era] = []
                        time_era_sorted[_time][era].append(name)

                # print(time_era_sorted)

                time_era_sorted_temp = {}
                for _time in time_era_sorted:
                    time_era_sorted_temp[_time] = {}
                    sorted_era = sorted([x for x in time_era_sorted[_time]], key=sort_relics)
                    for era in sorted_era:
                        time_era_sorted_temp[_time][era] = time_era_sorted[_time][era]

                time_era_sorted = time_era_sorted_temp.copy()
                del time_era_sorted_temp

                # print(time_era_sorted)

                embed_str_list = ['']
                for _time in time_era_sorted:
                    for era in time_era_sorted[_time]:
                        embed_str_list[-1] += f"**{era}:**\n"
                        for relic in time_era_sorted[_time][era]:
                            if f"{era} {relic} RELIC".upper() in get_rarest_relics():
                                embed_str_list[-1] += f"__{relic}__, "
                            else:
                                embed_str_list[-1] += f"{relic}, "
                        embed_str_list[-1] = embed_str_list[-1][:-2] + '\n'
                    embed_str_list.append('')

                # print(embed_str_list)

                for embed_str, _time in zip(embed_str_list, time_era_sorted):
                    embed.add_field(name=f"{_time} Days",
                                    value=embed_str,
                                    inline=True
                                    )

            await ctx.send(embed=embed)

        elif flags['sort_style'] == 'Sets':
            pass

        elif flags['sort_style'] == 'Price':
            pass

        elif flags['sort_style'] == 'Event':
            pass


    @tasks.loop(minutes=15)
    async def update_unvault_relics_db(self):
        await update_unvault_relics()

    @tasks.loop(minutes=1)
    async def auto_update_relic_spreadsheet(self):
        await check_for_website_update()

    @tasks.loop(hours=24)
    async def auto_update_steamcharts_info(self):
        await update_steamcharts_data()

    @tasks.loop(hours=24)
    async def auto_update_relic_dbs(self):

        th = threading.Thread(target=update_relic_dbs)
        th.start()


def setup(client):
    client.add_cog(Relic_Tools(client))
