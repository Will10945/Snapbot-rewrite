import time
from collections import OrderedDict
import re
import json
from copy import deepcopy
import discord
import asyncio

import relic_engine

from lib.utils.file_utils import new_relic_data, new_set_data, update_prime_access_dict, get_prime_junk, get_set_data, get_relic_data, \
                                 get_unvault_relic_sets, get_related_user_defaults, get_rarest_relics, get_meta_sets, update_relic_numbers


ERA_IMAGES = {
    'lith': 'https://images-ext-1.discordapp.net/external/Ufv1fP_0lTnkWZuWr_5ZCdkIWV9FR5jFp9GZJmKrDFE/https/cdn.discordapp.com/emojis/733657999931080734.png?width=75&height=92',
    'meso': 'https://images-ext-2.discordapp.net/external/wckhknsSFO7anuKPlYk4PT3OoW2_MobQNOvA9dIWVo0/https/cdn.discordapp.com/emojis/733658031841214504.png?width=75&height=93',
    'neo': 'https://images-ext-1.discordapp.net/external/p3JOLpP2ifXiKaRq6NAHBM-u3xi5dO3ZPnSWSSU7I3U/https/cdn.discordapp.com/emojis/733657853654728765.png?width=75&height=92',
    'axi': 'https://images-ext-2.discordapp.net/external/xrlLjw8Cbj0YKYdZmdtupw1hlkbz9h38ZxtOecXq4ZM/https/cdn.discordapp.com/emojis/732981038028030003.png?width=92&height=115',
}


def update_relic_dbs():
    time0 = time.perf_counter()

    # loop = asyncio.get_event_loop()
    # relic_data, set_data, _ = await loop.run_until_complete(relic_engine.build_json_files())
    relic_data, set_data = relic_engine.build_json_files()

    set_data = json.loads(json.dumps(set_data))
    relic_data = json.loads(json.dumps(relic_data))

    _update_pa_list(set_data)

    new_relic_data(relic_data)
    new_set_data(set_data)

    update_relic_numbers()

    time1 = time.perf_counter()
    print(f"Databases updated in: {time1-time0:0.1f} seconds")

def _update_pa_list(set_data):

    pa_dict = {}
    p_junk = get_prime_junk()

    for k, v in set_data.items():
        pa = (v['prime-access'] * ('N/A' not in v['prime-access'])) + ('Junk' * ('N/A' in v['prime-access']))
        if pa not in pa_dict:
            pa_dict[pa] = []
        if pa.lower() in p_junk:
            pa_dict['Junk'].append(k.split(' Prime')[0])
        elif pa not in k and k not in pa_dict[pa]:
            pa_dict[pa].append(k.split(' Prime')[0])

    pa_dict = dict(OrderedDict(sorted(pa_dict.items())))

    update_prime_access_dict(pa_dict)

def set_parse(args):

    set_list = list(get_set_data())
    args_iter = enumerate(args)

    sets = []

    for i, arg in args_iter:
        if arg == 'Prime':
            continue
        elif (_set := f"{arg} Prime") in set_list:
            sets.append(_set)
        elif (_set := f"{arg}") in 'Nami':
            sets.append('Nami Skyla Prime')
        elif (_set := f"{arg}") in 'Silva':
            sets.append('Silva & Aegis Prime')
        else:
            multi_word_set = ''
            for j, _arg in enumerate(args[i:(i+3 * (len(args) >= i+3) + len(args) * (len(args) < i+3))]):

                if _arg == 'And':
                    _arg = '&'

                multi_word_set += f"{_arg} "

                if (_m_set := f"{multi_word_set}Prime") in set_list:
                    sets.append(_m_set)
                    [next(args_iter) for _ in range(j)]
                    break

    return sets


def get_relic_4b4_avg(relic):

    relic_data = get_relic_data()

    best_price = 0
    for ref in relic_data[relic]:
        if (new_price := relic_data[relic][ref]['average_return']['4b4']) > best_price:
            best_price = int(new_price)

    return best_price


def find_relics_with_sets(sets, exclusive=True):

    relic_data = get_relic_data()

    relics_with_sets = {_set: [] for _set in sets}

    for relic in relic_data:
        drops = '__'.join(list(relic_data[relic]['Intact']['drops']))
        for _set in relics_with_sets:
            if _set in drops:
                relics_with_sets[_set].append(relic)

    final_list = []

    if exclusive:
        for _set in relics_with_sets:
            if not final_list:
                final_list = list(set(relics_with_sets[_set]))
            else:
                final_list = list(set(final_list) & set(relics_with_sets[_set]))

    elif not exclusive:
        for _set in relics_with_sets:
            final_list += relics_with_sets[_set]
        final_list = list(set(final_list))

    return final_list


def get_shared_relics(sets):

    relic_data = get_relic_data()
    relics = list(relic_data)

    for _set in sets:
        relics = [x for x in relics if _set in '__'.join(relic_data[x]['Intact']['drops'])]

    return relics


def flatten_dict(_dict, relic_list=None):
    if not relic_list:
        relic_list = []

    for k, v in _dict.items():
        if isinstance(v, dict):
            relic_list = flatten_dict(v, relic_list)
        else:
            relic_list += v

    return relic_list


def is_prime_junk(item):
    return item.title().split(' Prime')[0] in get_prime_junk()


def related_relics_manager(user_id, args):

    pass


def parse_related_relics(user_id, content):

    user_defaults = get_related_user_defaults()
    # args = re.split(', | |=|:', content.title())[1:]

    if str(user_id) not in user_defaults:
        user_defaults[str(user_id)] = {
            'sort_style': 'Time',
            'links': False,
            'average_return': 15,
            'set_price': 0,
            'price_threshold': 0,
            'threshold_increment': 10,
            'junk_amount': 6,
            'return_unvault': False,
            'unvault_sets': {},
            'rarest': False,
            'rarest_only': False,
            'sets': [],
            'relics': [],
            'concise': False,
            'detailed': False
        }

    flags = deepcopy(user_defaults[str(user_id)])

    flags['relics'].append(content[0].title())
    flags['return_unvault'] = content[1]
    flags['junk_amount'] = content[2]
    flags['sort_style'] = content[3]
    flags['links'] = content[4]
    flags['average_return'] = content[5]
    flags['price_threshold'] = content[6]
    flags['threshold_increment'] = content[7]
    flags['sets'] = get_meta_sets()

    relic_data = get_relic_data()

    rarest = [x.title().split(' Relic')[0] for x in get_rarest_relics()]
    unv_sets = get_unvault_relic_sets()

    for relic in flags['relics']:
        if relic in rarest:
            flags['rarest'] = True
        for _set in unv_sets:
            if relic in unv_sets[_set]:
                flags['unvault_sets'][_set] = unv_sets[_set]

        for part in relic_data[relic]['Intact']['drops']:
            if not is_prime_junk(part := part.split(' Prime')[0]) and part != 'Forma Blueprint':
                part not in flags['sets'] and flags['sets'].append(part)



    # print(json.dumps(flags, indent=4))
    return flags


def is_related():

    pass


def build_settings_embed(settings):

    settings_str = '\n'.join([f"{f'{x}:':12} {y}" for x, y in settings.items()])

    embed = discord.Embed(
        title='Relic Settings',
        description=f"```"
                    f"{settings_str}"
                    f"```"
    )

    return embed


class BuildRelics:

    def __init__(self):

        self.random = False
        self.random_override = False
        self.frames = []

        self.settings = {}




class FrameSelectModal(discord.ui.Modal, title='Choose Frames'):

    def __init__(self):
        super().__init__()

        self.random = True
        self.frames = []
        self.random_override = False

        frame_list = list([x.split()[0] for x, y in get_set_data().items() if y['type'] == 'Warframes'])
        frame_list_list = [frame_list[i:i+25] for i in range(0, len(frame_list), 25)]

        self.__random__ = discord.ui.Select(options=[discord.SelectOption(label=f"Yes"), discord.SelectOption(label=f"No")], placeholder='Random Frames?', min_values=0, max_values=1)
        super().add_item(self.__random__)

        self.__attributes__ = [self.__random__]
        for i, frl in enumerate(frame_list_list):
            setattr(self, f"select_frames_{i}", discord.ui.Select(options=[discord.SelectOption(label=f"{x}") for x in frl], min_values=0, max_values=len(frl), placeholder=f"Select Frames: ({frl[0]} - {frl[-1]})"))
            super().add_item(getattr(self, f"select_frames_{i}"))
            self.__attributes__.append(getattr(self, f"select_frames_{i}"))

    async def on_submit(self, interaction: discord.Interaction):

        if self.__attributes__[0].values and 'Yes' not in self.__attributes__[0].values:
            self.random = False

        if not self.__random__:
            self.frames = [x for y in self.__attributes__[1:] for x in y.values]

        if not self.frames:
            self.random = True
            self.random_override = True

        new_relics.frames = self.frames
        BuildRelics.random = self.random
        BuildRelics.random_override = self.random_override

        settings = {'Duplicates': 'No'}
        embed = build_settings_embed(settings)
        await interaction.response.send_message(f"Would you like to change any of the settings?", embed=embed, view=ChangeSettingsButtons(settings), ephemeral=True)



    # async def on_error(self, interaction: discord.Interaction, error: Exception):
    #     await interaction.response.send_message('Uh oh', ephemeral=True)


class RelicBuildOptionModal(discord.ui.Modal, title='Select Options'):

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.attributes = {}

        for setting, value in self.settings.items():
            setattr(self, setting, discord.ui.Select(options=[discord.SelectOption(label=f"Yes"), discord.SelectOption(label=f"No")], placeholder=setting))
            super().add_item(getattr(self, setting))
            self.attributes[setting] = getattr(self, setting)


    async def on_submit(self, interaction: discord.Interaction):
        for sett, value in self.attributes.items():
            self.settings[sett] = value.values[0]
        print(self.settings)
        BuildRelics.settings = self.settings

        await interaction.response.edit_message(content=f'Would you like to change any of the settings?', embed=build_settings_embed(self.settings), view=ChangeSettingsButtons(self.settings))

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message('Uh oh', ephemeral=True)


class RandomFramesButton(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = False

    @discord.ui.button(label='Random', style=discord.ButtonStyle.blurple)
    async def random_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()


class ChangeSettingsButtons(discord.ui.View):

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @discord.ui.button(label='Change', style=discord.ButtonStyle.blurple)
    async def change_settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RelicBuildOptionModal(self.settings))
        self.stop()

    @discord.ui.button(label='Build', style=discord.ButtonStyle.green)
    async def build_relics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"Building relics ...", embed=None, view=None)
        self.stop()
