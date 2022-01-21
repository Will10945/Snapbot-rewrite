import random

import discord
from lib.utils.file_utils import get_prime_access_list, get_gen_relics, get_gen_relics_data, get_set_data, get_relic_data

ERA_IMAGES = {
    'Lith': 'https://images-ext-1.discordapp.net/external/Ufv1fP_0lTnkWZuWr_5ZCdkIWV9FR5jFp9GZJmKrDFE/https/cdn.discordapp.com/emojis/733657999931080734.png?width=75&height=92',
    'Meso': 'https://images-ext-2.discordapp.net/external/wckhknsSFO7anuKPlYk4PT3OoW2_MobQNOvA9dIWVo0/https/cdn.discordapp.com/emojis/733658031841214504.png?width=75&height=93',
    'Neo': 'https://images-ext-1.discordapp.net/external/p3JOLpP2ifXiKaRq6NAHBM-u3xi5dO3ZPnSWSSU7I3U/https/cdn.discordapp.com/emojis/733657853654728765.png?width=75&height=92',
    'Axi': 'https://images-ext-2.discordapp.net/external/xrlLjw8Cbj0YKYdZmdtupw1hlkbz9h38ZxtOecXq4ZM/https/cdn.discordapp.com/emojis/732981038028030003.png?width=92&height=115',
}
PLATINUM = '<:platinum:897799994382352405>'
DUCATS = '<:ducat:897800009607684146>'

def get_era_images():
    return ERA_IMAGES

def gen_relics_parse(message):
    args = message.split()

    pa_dict = get_prime_access_list()

    flags = {
        'pa': [],
        'random': len(args) == 1,
        'randamt': 2,
        'dupe': True,
        'excal': False
    }

    for arg in args[1:]:

        if arg.lower() in ['random', 'rand']:
            flags['random'] = True
        if arg.isnumeric():
            flags['random'] = True
            flags['randamt'] = int(arg)
        elif arg.lower() in ['j', 'junk', 'trash', 't']:
            flags['dupe'] = False

        elif arg in ['excalibur', 'excal', 'lato', 'skana']:
            flags['excal'] = True
        elif arg.title() in pa_dict and arg.title() not in flags['pa']:
            flags['pa'].append(arg.title())
        else:
            for k, v in pa_dict.items():
                if arg.title() in v and k not in flags['pa']:
                    flags['pa'].append(k)

    if not flags['random'] and not flags['pa']:
        flags['random'] = True

    if flags['random']:
        pa_list = list(pa_dict)
        pa_list.remove('Junk')
        if flags['excal']:
            pa_list.append('Excalibur')
        for i in range(flags['randamt']):
            if not pa_list:
                break
            random.shuffle(pa_list)
            if (frame := pa_list.pop()) not in flags['pa']:
                flags['pa'].append(frame)

    elif flags['excal']:
        flags['pa'].append('Excalibur')

    flags['pa'].sort()

    return flags

def show_relics_parse(args):

    era = None
    gen_relics = list(get_gen_relics())
    valid_relics = []
    unused_args = []

    for arg in args:
        if len(valid_relics) >= 10:
            break
        if arg.title() in ['Lith', 'Meso', 'Neo', 'Axi']:
            era = arg.title()
        elif era:
            if (relic := f"{era} {arg.title()}") in gen_relics:
                valid_relics.append(relic)
            else:
                unused_args.append(arg.title())
        else:
            unused_args.append(arg.title())

    return valid_relics, unused_args


def create_relic_embed(relics):

    gen_relics = get_gen_relics()
    gen_relics_data = get_gen_relics_data()
    set_data = get_set_data()

    embed_list = []

    for relic in relics:

        rel_embed = discord.Embed(
            color=(discord.Color.dark_teal() if 'Lith' in relic else discord.Color.blue() if 'Meso' in relic
            else discord.Color.red() if 'Neo' in relic else discord.Color.gold())
        )
        rel_embed.set_author(name=relic, icon_url=ERA_IMAGES[relic.split()[0]])

        part_str = ''
        price_str = ''
        ducat_str = ''

        for partk, partv in gen_relics[relic].items():
            part_str += f"{'<:rare:897799950098915368>' * ('Rare' in partk) + '<:uncommon:897799965244534854>' * ('Uncommon' in partk) + '<:common:897799980402749461>' * ('Common' in partk)} " \
                        f"{partv}\n"

            if partv != 'Forma Blueprint':
                rarity = gen_relics_data[partv]['rarity value']
                try:
                    price_str += f"{PLATINUM} {set_data[partv.split('Prime')[0] + 'Prime']['parts'][partv]['plat']}\n"
                    ducat_str += f"{DUCATS} {100 if rarity == 5 else 65 if rarity == 4 else 45 if rarity == 3 else 25 if rarity == 2 else 15}\n"
                except:
                    price_str += f"{PLATINUM} {set_data[partv.split('Prime')[0] + 'Prime']['parts'][f'{partv} Blueprint']['plat']}\n"
                    ducat_str += f"{DUCATS} {100 if rarity == 5 else 65 if rarity == 4 else 45 if rarity == 3 else 25 if rarity == 2 else 15}\n"
            else:
                price_str += f"{PLATINUM} {0}\n"
                ducat_str += f"{DUCATS} {0}\n"

        rel_embed.add_field(name='Item', value=part_str, inline=True)
        rel_embed.add_field(name='Platinum', value=price_str, inline=True)
        rel_embed.add_field(name='Ducats', value=ducat_str, inline=True)

        embed_list.append(rel_embed)

    return embed_list


def parse_refinement(args):
    ref = None
    for arg in args:

        if arg in ['I', 'Int', 'Intact']:
            ref = 'Intact'
            break
        elif arg in ['E', 'Excep', 'Exceptional']:
            ref = 'Exceptional'
            break
        elif arg in ['F', 'Flaw', 'Flawless']:
            ref = 'Flawless'
            break
        elif arg in ['R', 'Rad', 'Radiant']:
            ref = 'Radiant'
            break

    if not ref:
        ref = 'Radiant'

    return ref


def calculate_averages(relics, refinement='Radiant'):

    if not refinement:
        refinement = 'Radiant'

    averages = []
    gen_relics = get_gen_relics()
    set_data = get_set_data()
    relic_ex = get_relic_data()['Axi A1']

    for rel in relics:

        total = [0, 0, 0, 0, 0]
        for partk, partv in gen_relics[rel].items():

            if 'Common' in partk:
                model = 'Trinity Prime Systems Blueprint'
            elif 'Uncommon' in partk:
                model = 'Akstiletto Prime Barrel'
            else:
                model = 'Nikana Prime Blueprint'

            for i, style in enumerate(['solo', '1b1', '2b2', '3b3', '4b4']):
                if 'Forma' not in partv:
                    try:
                        total[i] += set_data[f"{partv.split(' Prime')[0]} Prime"]['parts'][partv]['plat'] * relic_ex[refinement]['drops'][model]['calculated_chance'][style]
                    except:
                        total[i] += set_data[f"{partv.split(' Prime')[0]} Prime"]['parts'][f"{partv} Blueprint"]['plat'] * relic_ex[refinement]['drops'][model]['calculated_chance'][style]

        averages.append(total)

    return averages
