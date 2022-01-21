import time
from collections import OrderedDict
import re
import json
from copy import deepcopy

import relic_engine

from lib.utils.file_utils import new_relic_data, new_set_data, update_prime_access_dict, get_prime_junk, get_set_data, get_relic_data, \
                                 get_unvault_relic_sets, get_related_user_defaults, get_rarest_relics


ERA_IMAGES = {
    'lith': 'https://images-ext-1.discordapp.net/external/Ufv1fP_0lTnkWZuWr_5ZCdkIWV9FR5jFp9GZJmKrDFE/https/cdn.discordapp.com/emojis/733657999931080734.png?width=75&height=92',
    'meso': 'https://images-ext-2.discordapp.net/external/wckhknsSFO7anuKPlYk4PT3OoW2_MobQNOvA9dIWVo0/https/cdn.discordapp.com/emojis/733658031841214504.png?width=75&height=93',
    'neo': 'https://images-ext-1.discordapp.net/external/p3JOLpP2ifXiKaRq6NAHBM-u3xi5dO3ZPnSWSSU7I3U/https/cdn.discordapp.com/emojis/733657853654728765.png?width=75&height=92',
    'axi': 'https://images-ext-2.discordapp.net/external/xrlLjw8Cbj0YKYdZmdtupw1hlkbz9h38ZxtOecXq4ZM/https/cdn.discordapp.com/emojis/732981038028030003.png?width=92&height=115',
}


def update_relic_dbs():
    time0 = time.perf_counter()

    relic_data, set_data = relic_engine.build_json_files()

    set_data = json.loads(json.dumps(set_data))
    relic_data = json.loads(json.dumps(relic_data))

    _update_pa_list(set_data)

    new_relic_data(relic_data)
    new_set_data(set_data)

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
    args = re.split(', | |=|:', content.title())[1:]

    if str(user_id) not in user_defaults:
        user_defaults[str(user_id)] = {
            'sort_style': 'Time',
            'links': False,
            'average_return': 15,
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
    args_iter = iter(args)
    current = next(args_iter)

    relic_data = get_relic_data()
    unused_args = []

    while current:
        era = ''

        if current in ['Lith', 'Meso', 'Neo', 'Axi']:
            era = current
            up_next = next(args_iter, None)
            while re.match(r'[A-Z]\d{1,2}\Z', up_next):
                relic = f"{era} {up_next}"
                if relic in relic_data:
                    flags['relics'].append(relic)
                    up_next = next(args_iter, None)
                    if not up_next:
                        break
            current = up_next

        elif current in ['Style', 'S']:
            up_next = next(args_iter, None)
            if up_next in ['Time', 'Sets', 'Price', 'Event']:
                flags['sort_style'] = up_next
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Links', 'Link', 'L']:
            up_next = next(args_iter, None)
            if up_next in ['T', 'True']:
                flags['links'] = True
                current = next(args_iter, None)
                pass
            elif up_next in ['F', 'False']:
                flags['links'] = False
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Average', 'Return', 'Avg', 'Ret', 'A']:
            up_next = next(args_iter, None)
            if up_next.isnumeric():
                flags['average_return'] = int(up_next)
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Threshold', 'Start', 'Begin', 'Initial', 'Init', 'T']:
            up_next = next(args_iter, None)
            if up_next.isnumeric():
                flags['price_threshold'] = int(up_next)
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Increment', 'Increase', 'Inc', 'I']:
            up_next = next(args_iter, None)
            if up_next.isnumeric():
                flags['threshold_increment'] = int(up_next)
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Junk', 'Trash', 'J']:
            up_next = next(args_iter, None)
            if up_next.isnumeric():
                flags['junk_amount'] = int(up_next) * int(up_next) < 6 + 5 * int(up_next) >= 6
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Unvault', 'U']:
            up_next = next(args_iter, None)
            if up_next in ['T', 'True']:
                flags['return_unvault'] = True
                current = next(args_iter, None)
                pass
            elif up_next in ['F', 'False']:
                flags['return_unvault'] = False
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Concise', 'Short', 'Small', 'C']:
            up_next = next(args_iter, None)
            if up_next in ['T', 'True']:
                flags['concise'] = True
                current = next(args_iter, None)
                pass
            elif up_next in ['F', 'False']:
                flags['concise'] = False
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Detailed', 'Detail', 'D']:
            up_next = next(args_iter, None)
            if up_next in ['T', 'True']:
                flags['detailed'] = True
                current = next(args_iter, None)
                pass
            elif up_next in ['F', 'False']:
                flags['detailed'] = False
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        elif current in ['Rarest', 'Rare', 'R']:
            up_next = next(args_iter, None)
            if up_next in ['T', 'True']:
                flags['rarest_only'] = True
                current = next(args_iter, None)
                pass
            elif up_next in ['F', 'False']:
                flags['rarest_only'] = False
                current = next(args_iter, None)
                pass
            else:
                current = up_next

        else:
            unused_args.append(current)
            current = next(args_iter, None)

    flags['sets'] = set_parse(unused_args)

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
                flags['sets'].append(part)



    # print(json.dumps(flags, indent=4))
    return flags


def is_related():

    pass
