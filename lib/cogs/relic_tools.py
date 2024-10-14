import asyncio

import discord
from datetime import datetime, time, timedelta

from concurrent.futures.thread import ThreadPoolExecutor

# import relic_engine
from discord.ext import commands, tasks
from discord import app_commands, ui
from discord.app_commands import Range
from typing import Optional, List, Union
from discord.errors import HTTPException

from lib.utils.file_utils import get_rarest_relics, get_set_data, get_relic_data, get_unvault_relic_sets
from lib.utils.relic_utils import update_relic_dbs, set_parse, find_relics_with_sets, get_shared_relics, flatten_dict, is_prime_junk, \
                                  parse_related_relics, ERA_IMAGES, FrameSelectModal, BuildRelics
from lib.utils.spreadsheet_utils import check_for_website_update, availability_parser, availability_manager, update_steamcharts_data, parse_vault_order, \
                                        find_vault_order, update_unvault_relics, find_unvault_sets, get_full_sheet, sort_relics, is_related, related_sort_manager, \
                                        get_overlapping_relics, auto_update_vault_date_order, get_vault_date_order


# @app_commands.command(name='related', description='Get related relics')
# @app_commands.guilds(824288433517232149)
# async def related_relics_slash(self, interaction: discord.Interaction,
#                                relic: str,
#                                unvault: Optional[bool] = False,
#                                junk: Optional[Range[0, 6]] = 0,
#                                sort: Optional[str] = 'price',
#                                links: Optional[bool] = False,
#                                avg_return: Optional[int] = 10,
#                                initial_price: Optional[int] = 1,
#                                increment: Optional[int] = 1,
#                                sets: Optional[list] = []
#                                ):


# class Related_Relics(ui.Modal, title='Related Relics'):
#     relic = ui.Select(options=[discord.SelectOption(label=x, value=x) for x in list(get_relic_data())[:24]], placeholder=f'Choose a Relic')
#     # relic_choice = ui.Select(options=list(get_relic_data()))
#
#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.send_message(f"{self.relic}")



class Relic_Tools(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_ready(self):

        self.auto_update_relic_spreadsheet.start().set_name('auto_update_relic_spreadsheet')
        self.auto_update_steamcharts_info.start().set_name('auto_update_steamcharts_info')

        self.update_unvault_relics_db.start()

        self.auto_update_vault_date_db.start()

        time_until_midnight = (datetime.combine(datetime.today(), time.min) + timedelta(days=1)).timestamp() - datetime.now().timestamp()
        print(f"Auto Update Relics DB job added and starting in: {time_until_midnight:0.1f}s")
        # await asyncio.sleep(time_until_midnight)
        self.auto_update_relic_dbs.start()
        update_relic_dbs()
        print("Updated Relics DB")

        self.client.cogs_ready.ready_up('relic_tools')


    @app_commands.command(name='update_relic_dbs',
                          description='Updates relic databases')
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guilds(824288433517232149)
    async def force_update_relic_dbs_slash(self, interaction: discord.Interaction):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, update_relic_dbs)
        await interaction.response.send_message('Relic databases updated')


    @app_commands.command(name='unvaults', description='Shows frame vault order by date')
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    # @app_commands.guilds(780376195182493707)
    async def unvaults_slash(self, interaction: discord.Interaction, frame: Optional[str] = None):

        if frame:
            frame = frame.split(' Prime')[0]
            # print(frame)
            sets = parse_vault_order([frame])
            # print(f"{sets}")
            valid_unvaults = find_unvault_sets(sets)
            # print(f"{valid_unvaults}")
            unv_embed = None

            if not valid_unvaults:
                await interaction.response.send_message(f"No valid frames as command parameters")
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

            await interaction.response.send_message(embed=unv_embed)

        else:
            ordered_unvaults, active = find_vault_order()

            if not ordered_unvaults or not active:
                await interaction.response.send_message(f"Data not updated, try again in a few seconds")
                return

            print_str = 'Data not updated, check the bottom of:\n[Relic Spreadsheet](https://docs.google.com/spreadsheets/d/1lHt3CaaCEdNR1ZSH8BaWFERMFHnxSkpGxQV4R_CiSyI/edit?usp=sharing)\n\n'
            for k, v in ordered_unvaults.items():
                k_date = f"<t:{int((datetime.strptime(k, '%b %d %Y') + timedelta(hours=14)).timestamp())}:R>"
                # days = (datetime.now() - k_date).days if (datetime.now() - k_date).days != 0 else 1
                print_str += f"{k_date}: {', '.join(v)}\n"

            k_dates = {}
            for frame, timestamp in active.items():
                if (formatted_time := f"<t:{int((timestamp + timedelta(hours=14)).timestamp())}:R>") not in k_dates:
                    k_dates[formatted_time] = []
                k_dates[formatted_time].append(frame)
            for timestamp, frames in k_dates.items():
                print_str += f"\n*Ongoing since {timestamp} : {', '.join(frames)}*"

            await interaction.response.send_message(print_str)


    @app_commands.command(name='vaults', description='Shows frame vault order by date')
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    async def get_vault_order(self, interaction: discord.Interaction):

        await interaction.response.send_message(embed=get_vault_date_order())


    @unvaults_slash.autocomplete('frame')
    async def frame_autocomplete(self,
                                 interaction: discord.Interaction,
                                 current: str
                                 ) -> List[app_commands.Choice[str]]:
        frames = [k for k, v in get_set_data().items() if v['type'] == 'Warframes']
        return [app_commands.Choice(name=frame, value=frame) for frame in frames if current.lower() in frame.lower()]


    @app_commands.command(name='shared', description='Shows relics that share parts for the given sets')
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    # @app_commands.guilds(780376195182493707)
    async def shared_relics_slash(self, interaction: discord.Interaction,
                                  set_1: str, set_2: str, set_3: Optional[str] = '__',
                                  set_4: Optional[str] = '__', set_5: Optional[str] = '__', set_6: Optional[str] = '__'
                                  ):

        # await interaction.response.send_message(f"{set1} {set2} {set3} {set4} {set5} {set6}")

        sets = [set_1, set_2, set_3, set_4, set_5, set_6]
        relics = find_relics_with_sets(sets, exclusive=True)
        sets = [_set.split(' Prime')[0] for _set in sets]

        if relics:
            embed = discord.Embed(
                title='Shared Relics',
                description=f"Relics shared by the following sets:\n**{', '.join([x for x in sets if x != '__'])}**"
            )
            embed.add_field(name='Relics', value='\n'.join(relics), inline=True)
        else:
            embed = discord.Embed(
                title='Shared Relics',
                description=f"No relics shared by the following sets:\n**{', '.join([x for x in sets if x != '__'])}**"
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='average_top', description='Shows relics that share parts for the given sets')
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    async def average_all_relics(self, interaction: discord.Interaction,
                                 set: Optional[str] = None,
                                 era: Optional[str] = None,
                                 refinement: Optional[str] = "Radiant",
                                 style: Optional[str] = '4b4',
                                 vaulted: Optional[str] = 'True',
                                 sort: Optional[str] = 'Descending',
                                 amount: Optional[str] = '10'):

        vaulted = 'True' == vaulted.title() or 'T' == vaulted.title()
        refinement = refinement.title()

        if amount.isnumeric():
            amount = int(amount)
            if amount > 25:
                amount = 25

        relics_dict = get_relic_data()
        if not era:
            relics = list(relics_dict)
        else:
            era = era.title()
            relics = [x for x in relics_dict if era in x]

        _set = set
        if _set:
            set_relics = []
            if _set in get_set_data():
                for relic in relics:
                    if _set in [f"{y.split('Prime ')[0]}Prime" for y in relics_dict[relic]['Intact']['drops']]:
                        set_relics.append(relic)
            else:
                _set = None

            relics = set_relics

        if not vaulted:
            relics = [x for x in relics if not relics_dict[x]['Intact']['vaulted']]

        best_prices = [relics_dict[x][refinement]['average_return'][style] for x in relics]
        relic_prices = {x: y for x, y in zip(relics, best_prices)}
        relic_prices = {k: f"<:platinum:897799994382352405> {int(v)}" for k, v in sorted(relic_prices.items(), key=lambda item: item[1], reverse=not (sort == '+' or sort.title() in 'Ascending'))}

        relic_prices = list(relic_prices.items())[:amount]

        embed = discord.Embed(
            description=f"```{'Set:':14} {_set if _set else 'N/A'}\n"
                        f"{'Era:':14} {era if era else 'All'}\n"
                        f"{'Refinement:':14} {refinement}\n"
                        f"{'Style:':14} {style}\n"
                        f"{'Vaulted Only:':14} {vaulted}\n"
                        f"{'Sorted:':14} {sort}\n"
                        f"{'Total Shown:':14} {amount}```"
        )
        embed.set_author(name=f"Highest Average Values", icon_url=ERA_IMAGES[era] if era else None)
        embed.add_field(name="Relics", value='\n'.join([x[0] for x in relic_prices]), inline=True)
        embed.add_field(name="Value", value='\n'.join([x[1] for x in relic_prices]), inline=True)

        try:
            await interaction.response.send_message(embed=embed)
        except HTTPException:
            await interaction.response.send_message(f"No relics fit the given parameters :(")

    @average_all_relics.autocomplete('era')
    async def era_autocomplete(self,
                               interaction: discord.Interaction,
                               current: str
                               ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=era, value=era) for era in ['Lith', 'Meso', 'Neo', 'Axi'] if current.title() in era][:24]


    @average_all_relics.autocomplete('refinement')
    async def refinement_autocomplete(self,
                                      interaction: discord.Interaction,
                                      current: str
                                      ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=ref, value=ref) for ref in ['Intact', 'Exceptional', 'Flawless', 'Radiant'] if current.title() in ref][:24]


    @average_all_relics.autocomplete('style')
    async def style_autocomplete(self,
                                 interaction: discord.Interaction,
                                 current: str
                                 ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=sty, value=sty) for sty in ['1b1', '2b2', '3b3', '4b4'] if current.title() in sty][:24]

    @average_all_relics.autocomplete('vaulted')
    async def vaulted_autocomplete(self,
                                 interaction: discord.Interaction,
                                 current: str
                                 ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=vau, value=vau) for vau in ['True', 'False'] if current.title() in vau][:24]

    @average_all_relics.autocomplete('sort')
    async def sort_autocomplete(self,
                                   interaction: discord.Interaction,
                                   current: str
                                   ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=sort, value=sort) for sort in ['Ascending', 'Descending'] if current.title() in sort][:24]

    @average_all_relics.autocomplete('set')
    async def set_autocomplete(self,
                               interaction: discord.Interaction,
                               current: str
                               ) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=_set.split(' Prime')[0], value=_set) for _set in get_set_data().keys() if current.title() in _set][:24]


    @shared_relics_slash.autocomplete('set_1')
    @shared_relics_slash.autocomplete('set_2')
    @shared_relics_slash.autocomplete('set_3')
    @shared_relics_slash.autocomplete('set_4')
    @shared_relics_slash.autocomplete('set_5')
    @shared_relics_slash.autocomplete('set_6')
    async def set_autocomplete(self,
                               interaction: discord.Interaction,
                               current: str
                               ) -> List[app_commands.Choice[str]]:
        frames = [k for k, v in get_set_data().items()]
        return [app_commands.Choice(name=frame, value=frame) for frame in frames if current.lower() in frame.lower()][:24]


    @app_commands.command(name='availability', description='Get relic availability')
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    # @app_commands.guilds(780376195182493707)
    async def relic_availability_slash(self, interaction: discord.Interaction,
                                 relic_1: str, relic_2: Optional[str] = '__', relic_3: Optional[str] = '__',
                                 relic_4: Optional[str] = '__', relic_5: Optional[str] = '__'):

        relics = await availability_parser([relic_1, relic_2, relic_3, relic_4, relic_5])

        if not relics:
            await interaction.response.send_message(f"Not a valid relic.\nIf it doesn't show up in the autofill list then it doesn't exist :)", ephemeral=True)
            return

        av_embed = await availability_manager(relics)
        imgfile = discord.File('./data/plot_image.png', filename='plot_image.png')
        av_embed.set_image(url='attachment://plot_image.png')

        if interaction.channel_id not in [780377679227650079, 824288433966809089]:
            await interaction.response.send_message(embed=av_embed, file=imgfile)
            return
        await interaction.response.send_message(file=imgfile)


    @app_commands.command(name='related', description='Get related relics')
    @app_commands.describe(increment='Prices increment at a rate of: initial_price + (avg_return / increment). default = 10',
                           initial_price='The starting price for relics when links is set to True. default = 1',
                           avg_return='Only shows relics with an average return above this value. default = 10',
                           links='Shows the relics as links with prices for quick copying and pasting into game. default = False',
                           junk='Limit the amount of junk allowed in relics. default = 6 (ANY RELIC)',
                           unvault='Toggle ON to only show unvault relics. default = False',
                           relic='Choose a relic to compare relics to. REQUIRED',
                           # sort='Sorting style for the final output. default = time'
                           )
    @app_commands.guilds(824288433517232149, 780376195182493707, 780199960980750376)
    # @app_commands.guilds(780376195182493707)
    async def related_relics_slash(self, interaction: discord.Interaction,
                                   relic: str,
                                   unvault: Optional[bool] = False,
                                   junk: Optional[Range[int, 0, 6]] = 6,
                                   # sort: Optional[str] = 'Time',
                                   links: Optional[bool] = False,
                                   avg_return: Optional[int] = 10,
                                   initial_price: Optional[int] = 1,
                                   increment: Optional[int] = 10,
                                   # sets: Optional[list] = []
                                   ):

        flags = parse_related_relics(interaction.user.id, [relic, unvault, junk, 'Time', links, avg_return, initial_price, increment])

        # flags['relics'] = get_overlapping_relics(flags['relics'])

        if not flags['relics']:
            await interaction.response.send_message('You must provide at least one valid relic.')
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

            await interaction.response.send_message(embed=embed)

        else:
            related_relics_time, related_relics_sets, related_relics_price, related_relics_event, related_relics_links = related_sort_manager(flags)

            embeds = [
                discord.Embed(
                    description=f"**Parameters:**\n" +
                                (f"Sort Style: `{flags['sort_style']}`\n" if not flags['links'] else '') +
                                (f"Starting Price: `{flags['price_threshold']}`\n" if flags['links'] else '') +
                                (f"Increment at: `{flags['threshold_increment']}`\n" if flags['links'] else '') +
                                (f"Average Return: `{flags['average_return']}`\n" if True else '') +
                                (f"Min Set Price: `{flags['set_price']}`\n" if flags['sort_style'] in ['Sets'] else '') +
                                (f"Junk Amount: `{flags['junk_amount']}`\n" if flags['sort_style'] not in ['Sets'] else '') +
                                (f"Unvault Relics Only: `{flags['return_unvault']}`\n" if True else '') +
                                (f"Rarest Relics Only: `{flags['rarest']}`\n" if True else '') +
                                (f"Detailed: `{flags['detailed']}`\n\n" if False else ''),
                                # f"For more info on parameters, check out `s!help related`"
                    color=(discord.Color.teal() if 'lith' in relic_era.lower() else discord.Color.blue() if 'meso' in relic_era.lower()
                    else discord.Color.red() if 'neo' in relic_era.lower() else discord.Color.gold())
                )
            ]
            embeds[-1].set_author(
                name=flags['relics'][0],
                icon_url=ERA_IMAGES[relic_era]
            )

            if related_relics_links:

                for i, link_msg in enumerate(related_relics_links):
                    if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                        await self.create_embed(flags, relic_era)

                    embeds[-1].add_field(
                        name=f"Links {i+1}",
                        value=link_msg,
                        inline=False
                    )

            elif related_relics_time:

                time_sorted = {}
                for relic, span in related_relics_time['totals'].items():
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

                time_era_sorted_temp = {}
                for _time in time_era_sorted:
                    time_era_sorted_temp[_time] = {}
                    sorted_era = sorted([x for x in time_era_sorted[_time]], key=sort_relics)
                    for era in sorted_era:
                        time_era_sorted_temp[_time][era] = time_era_sorted[_time][era]

                time_era_sorted = time_era_sorted_temp.copy()
                del time_era_sorted_temp

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

                for embed_str, _time in zip(embed_str_list, time_era_sorted):
                    if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                        await self.create_embed(flags, relic_era)

                    embeds[-1].add_field(
                        name=f"{_time} Days",
                        value=embed_str,
                        inline=True
                    )

            elif related_relics_sets:

                sets = sorted(list(related_relics_sets))
                embed_str = ['']

                for _set in sets:
                    for relic in related_relics_sets[_set]:
                        era = relic.split(' ')[0]
                        name = relic.split(' ')[1]
                        if era not in embed_str[-1]:
                            embed_str[-1] = embed_str[-1][:-2]
                            embed_str[-1] += f"\n**{era}**\n"
                        if f"{relic} RELIC".upper() in get_rarest_relics():
                            embed_str[-1] += f"__{name}__, "
                        else:
                            embed_str[-1] += f"{name}, "
                    embed_str[-1] = embed_str[-1][:-2]
                    embed_str.append('')

                # print(embed_str)



                for _set, _str in zip(sets, embed_str):

                    if flags['set_price'] <= get_set_data()[f"{_set} Prime"]['plat']:

                        if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                            embeds.append(await self.create_embed(flags, relic_era))

                        embeds[-1].add_field(
                            name=_set,
                            value=_str,
                            inline=True
                        )

                pass

            elif related_relics_price:
                pass

            elif related_relics_event:
                pass

            for embed in embeds:
                await interaction.response.send_message(embed=embed)


    @relic_availability_slash.autocomplete('relic_1')
    @relic_availability_slash.autocomplete('relic_2')
    @relic_availability_slash.autocomplete('relic_3')
    @relic_availability_slash.autocomplete('relic_4')
    @relic_availability_slash.autocomplete('relic_5')
    @related_relics_slash.autocomplete('relic')
    async def set_autocomplete(self,
                               interaction: discord.Interaction,
                               current: str
                               ) -> List[app_commands.Choice[str]]:
        relics = list(get_relic_data())
        return [app_commands.Choice(name=relic, value=relic) for relic in relics if current.lower() in relic.lower()][:24]

    # @app_commands.command(name='related', description='Get related relics')
    # @app_commands.guilds(824288433517232149)
    # async def related_relics_slash(self, interaction: discord.Interaction):
    #     await interaction.response.send_modal(Related_Relics())


    @app_commands.command(name='build', description='build relics')
    @app_commands.guilds(824288433517232149, 780376195182493707)
    async def build_relics(self,
                           interaction: discord.Interaction):

        new_relics = BuildRelics()
        new_modal = FrameSelectModal()

        await interaction.response.send_modal(new_modal)


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

        if len(ctx.message.content.split()) == 1:
            await ctx.send('You must provide at least one valid relic.')
            return

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

        else:

            related_relics_time, related_relics_sets, related_relics_price, related_relics_event, related_relics_links = related_sort_manager(flags)

            embeds = [
                discord.Embed(
                    description=f"**Parameters:**\n" +
                                (f"Sort Style: `{flags['sort_style']}`\n" if not flags['links'] else '') +
                                (f"Starting Price: `{flags['price_threshold']}`\n" if flags['links'] else '') +
                                (f"Increment at: `{flags['threshold_increment']}`\n" if flags['links'] else '') +
                                (f"Average Return: `{flags['average_return']}`\n" if True else '') +
                                (f"Min Set Price: `{flags['set_price']}`\n" if flags['sort_style'] in ['Sets'] else '') +
                                (f"Junk Amount: `{flags['junk_amount']}`\n" if flags['sort_style'] not in ['Sets'] else '') +
                                (f"Unvault Relics Only: `{flags['return_unvault']}`\n" if True else '') +
                                (f"Rarest Relics Only: `{flags['rarest']}`\n" if True else '') +
                                (f"Detailed: `{flags['detailed']}`\n\n" if False else '') +
                                f"For more info on parameters, check out `s!help related`",
                    color=(discord.Color.teal() if 'lith' in relic_era.lower() else discord.Color.blue() if 'meso' in relic_era.lower()
                    else discord.Color.red() if 'neo' in relic_era.lower() else discord.Color.gold())
                )
            ]
            embeds[-1].set_author(
                name=flags['relics'][0],
                icon_url=ERA_IMAGES[relic_era]
            )

            if related_relics_links:

                for i, link_msg in enumerate(related_relics_links):
                    if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                        await self.create_embed(flags, relic_era)

                    embeds[-1].add_field(
                        name=f"Links {i+1}",
                        value=link_msg,
                        inline=False
                    )

            elif related_relics_time:

                time_sorted = {}
                for relic, span in related_relics_time['totals'].items():
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

                time_era_sorted_temp = {}
                for _time in time_era_sorted:
                    time_era_sorted_temp[_time] = {}
                    sorted_era = sorted([x for x in time_era_sorted[_time]], key=sort_relics)
                    for era in sorted_era:
                        time_era_sorted_temp[_time][era] = time_era_sorted[_time][era]

                time_era_sorted = time_era_sorted_temp.copy()
                del time_era_sorted_temp

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

                for embed_str, _time in zip(embed_str_list, time_era_sorted):
                    if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                        await self.create_embed(flags, relic_era)

                    embeds[-1].add_field(
                        name=f"{_time} Days",
                        value=embed_str,
                        inline=True
                    )

            elif related_relics_sets:

                sets = sorted(list(related_relics_sets))
                embed_str = ['']

                for _set in sets:
                    for relic in related_relics_sets[_set]:
                        era = relic.split(' ')[0]
                        name = relic.split(' ')[1]
                        if era not in embed_str[-1]:
                            embed_str[-1] = embed_str[-1][:-2]
                            embed_str[-1] += f"\n**{era}**\n"
                        if f"{relic} RELIC".upper() in get_rarest_relics():
                            embed_str[-1] += f"__{name}__, "
                        else:
                            embed_str[-1] += f"{name}, "
                    embed_str[-1] = embed_str[-1][:-2]
                    embed_str.append('')

                # print(embed_str)



                for _set, _str in zip(sets, embed_str):

                    if flags['set_price'] <= get_set_data()[f"{_set} Prime"]['plat']:

                        if len(embeds[-1].fields) >= 25 * len(embeds) - len(embeds):
                            embeds.append(await self.create_embed(flags, relic_era))

                        embeds[-1].add_field(
                            name=_set,
                            value=_str,
                            inline=True
                        )

                pass

            elif related_relics_price:
                pass

            elif related_relics_event:
                pass

            for embed in embeds:
                await ctx.send(embed=embed)


    async def create_embed(self, flags, relic_era):

        embed = discord.Embed(
            color=(discord.Color.teal() if 'lith' in relic_era.lower() else discord.Color.blue() if 'meso' in relic_era.lower()
                   else discord.Color.red() if 'neo' in relic_era.lower() else discord.Color.gold())
        )
        embed.set_author(
            name=f"{flags['relics'][0]} Continued",
            icon_url=ERA_IMAGES[relic_era]
        )

        return embed

    @tasks.loop(minutes=15)
    async def update_unvault_relics_db(self):
        while not get_full_sheet():
            await asyncio.sleep(1)
        await update_unvault_relics()

    @tasks.loop(minutes=1)
    async def auto_update_relic_spreadsheet(self):
        await check_for_website_update()

    @tasks.loop(hours=24)
    async def auto_update_steamcharts_info(self):
        await update_steamcharts_data()

    @tasks.loop(hours=24)
    async def auto_update_relic_dbs(self):
        await self.client.loop.run_in_executor(ThreadPoolExecutor(), update_relic_dbs)

    @tasks.loop(hours=24)
    async def auto_update_vault_date_db(self):
        while not get_full_sheet():
            await asyncio.sleep(1)
        await auto_update_vault_date_order()



async def setup(client):
    await client.add_cog(Relic_Tools(client))
