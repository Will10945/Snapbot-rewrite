import asyncio
import datetime
from dateutil.relativedelta import relativedelta
import re
import gspread_asyncio
import discord
import aiohttp
import json

from bs4 import BeautifulSoup as Soup
from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
from google.oauth2.service_account import Credentials

from lib.utils.file_utils import get_relic_data, get_set_data, get_unvault_relic_sets, update_unvault_relic_sets, get_prime_junk, get_rarest_relics, \
                                 get_vault_dates, update_vault_dates
from lib.utils.relic_utils import get_relic_4b4_avg

RELIC_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1lHt3CaaCEdNR1ZSH8BaWFERMFHnxSkpGxQV4R_CiSyI/edit?usp=sharing"


def get_creds():

    creds = Credentials.from_service_account_file('./data/service_account.json')
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return scoped


steamcharts_data = {}

agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
full_sheet = []
spreadsheet_ranges = {
    'relics': [1, 0],
    'baro': [0, 0],
    'baro_history': [0, 0],
    'baro_link': [0, 0],
    'railjack': [0, 0],
    'updates': [0, 0]
}
PATCH = 0
EVENT = 1
RELICS_IN = 2
RELICS_OUT = 3
TOTAL_RELICS = 4
PRIME_ACCESS_GROUPS = 7

BARO_RELIC_DATES = 1
BARO_RELICS = 2

RJ_RELICS = 2
RJ_EVENT = 1

UPDATE_NUMBER = 0
UPDATE_CONTEXT = 1

SCHARTS_DATES = []
SCHARTS_VALUES = []
SCHARTS_AVERAGE = []

COLORS = list(mcolors.BASE_COLORS)


def atoi(text):
    return int(text) if text.isdigit() else text

def sort_relics(relic):
    return [atoi(c) for c in re.split(r'(\d+)', f"{'Z' * ('Axi' in relic)}{relic}")]


def get_full_sheet():
    return full_sheet


async def update_unvault_relics():

    set_data = get_set_data()
    frame_list = [x.split(' Prime')[0] for x in list(set_data) if set_data[x]['type'] == 'Warframes']

    start_frames = {}
    end_frames = {}
    for row in full_sheet[spreadsheet_ranges['relics'][0]:spreadsheet_ranges['relics'][1]]:
        if datetime.datetime.strptime(row[EVENT].split(': ')[0].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' '), '%B %d %Y') > datetime.datetime.now():
            break
        temp_vaulted = {}
        release_index = 0
        vault_index = 0
        start_index = 0
        end_index = 0
        in_index = 0
        out_index = 0
        for i, word in enumerate(row[EVENT].split()):
            word = word.replace('(', '').replace(')', '').replace(',', '')
            if word in frame_list:
                temp_vaulted[word] = i
            if 'Start' in word:
                start_index = i
            if 'Release' in word:
                release_index = i
            if 'End' in word:
                end_index = i
            if 'Vault' in word:
                vault_index = i
            if 'In:' in word:
                in_index = i
            if 'Out:' in word:
                out_index = i


        valid_start_frames = []
        valid_end_frames = []
        start_relics = []
        end_relics = []
        for frame, index in temp_vaulted.items():

            if index < end_index or (out_index < index and out_index):
                valid_end_frames.append(frame)
                if not end_relics:
                    end_relics = row[RELICS_OUT].split(', ')

            if end_index < index < start_index or ((in_index < index and (in_index and not out_index)) or (in_index < index < out_index if out_index else False)):
                valid_start_frames.append(frame)
                if not start_relics:
                    start_relics = row[RELICS_IN].split(', ')

        if valid_start_frames:
            start_frames[', '.join(sorted(valid_start_frames))] = start_relics
        if valid_end_frames:
            end_frames[', '.join(sorted(valid_end_frames))] = end_relics

    final_frames = {}
    for start, end in zip(list(start_frames), list(end_frames)):
        final_frames[start] = sorted(list(set.intersection(set(start_frames[start]), set(end_frames[end]))), key=sort_relics)

    update_unvault_relic_sets(final_frames)


async def check_for_website_update(force_rebuild=False):
    global spreadsheet_ranges, full_sheet

    agc = await agcm.authorize()
    # print(f"{agc}")
    sheet = await agc.open_by_url(RELIC_SPREADSHEET_URL)
    # print(f"{sheet}")
    worksheet = await sheet.get_worksheet(0)
    # print(f"{worksheet}")
    full_sheet = await worksheet.get_all_values()
    # print(f"{full_sheet}")

    category = 'relics'
    prev_row = ''
    for i, row in enumerate(full_sheet):
        cur_row = ''.join(row)

        if cur_row and not prev_row and i:
            category = '_'.join(row[0].lower().split())
            spreadsheet_ranges[category][0] = i

        if not cur_row and prev_row:
            spreadsheet_ranges[category][1] = i

        prev_row = cur_row

    spreadsheet_ranges[category][1] = len(full_sheet)


async def update_steamcharts_data():
    global SCHARTS_DATES, SCHARTS_VALUES, SCHARTS_AVERAGE

    async with aiohttp.ClientSession() as session:
        async with session.get("https://steamcharts.com/app/230410#All") as response:
            text = await response.read()

    s = Soup(text.decode('utf-8'), 'lxml')

    tr_list = [t.find_all("td") for t in s.find_all('tr')]
    tr_list = [x for x in tr_list if x]

    for j, x in enumerate(tr_list):
        for k, y in enumerate(x):
            if isinstance(y, str):
                tr_list[j][k] = y.replace('\n', '').replace('\t', '')
            else:
                tr_list[j][k] = y.text.replace('\n', '').replace('\t', '')
        steamcharts_data[x[0]] = float(x[1])

    dates = list(steamcharts_data.keys())[::-1]
    conversion_index = list(dates).index('July 2016')
    SCHARTS_VALUES = list(steamcharts_data.values())[::-1][conversion_index:]

    dates = dates[conversion_index:]
    dates[-1] = datetime.datetime.today().strftime("%B %Y")
    SCHARTS_DATES = [datetime.datetime.strptime(x, '%B %Y') for x in dates]

    SCHARTS_AVERAGE = [sum(SCHARTS_VALUES[(x - 12 if x > 12 else 0):x + 1]) / ((x + 1) if x <= 12 else 12) for x in range(len(SCHARTS_VALUES))]

async def availability_parser(args):

    all_relics = list(get_relic_data())
    valid_relics = []

    args = [x.title() for x in args]

    for arg in args:
        if arg in all_relics and arg not in valid_relics:
            valid_relics.append(arg)

    return valid_relics


def get_availability_dict(relics):
    relic_locations = {}

    for rel in relics:
        relic_locations[rel] = {
            'type': [],
            'release': [],
            'cycles': [],
            'vault': [],
            'available': [],
            'baro': [],
            'railjack': []
        }

    for relic in relics:
        cycles = 0
        for i, row in enumerate(full_sheet):

            if relic in row[RELICS_IN].split(', ') and i < spreadsheet_ranges['relics'][1]:
                relic_locations[relic]['release'].append(i)
                event = ''
                if 'Vault' in full_sheet[i][EVENT] or 'Conversion' in full_sheet[i][EVENT]:
                    event += 'Regular '
                if 'Start' in full_sheet[i][EVENT]:
                    event += 'Unvault '
                if 'Anniversary' in full_sheet[i][EVENT]:
                    event += 'Event '
                if 'Resurgence' in full_sheet[i][EVENT]:
                    event += 'Resurgence '
                relic_locations[relic]['type'].append(event.strip())
            elif relic in row[RELICS_OUT].split(', ') and i < spreadsheet_ranges['relics'][1]:
                relic_locations[relic]['vault'].append(i)
                relic_locations[relic]['available'].append(False)

            elif relic in row[RJ_RELICS].split(', ') and i < spreadsheet_ranges['railjack'][1]:
                relic_locations[relic]['railjack'].append(i)
            elif relic in row[BARO_RELICS].split(', ') and i < spreadsheet_ranges['baro_history'][1]:
                relic_locations[relic]['baro'].append(i)

            elif len(relic_locations[relic]['vault']) < len(relic_locations[relic]['release']) and spreadsheet_ranges['relics'][1] == i:
                relic_locations[relic]['vault'].append(i - 1)
                relic_locations[relic]['available'].append(True)

            if 'Regular' in relic_locations[relic]['type']:
                if (len(relic_locations[relic]['release']) > len(relic_locations[relic]['vault'])
                        and 'Vault' in row[EVENT] and relic not in ['Lith M1', 'Meso B1', 'Neo D1', 'Axi V2']):
                    cycles += 1
                elif len(relic_locations[relic]['release']) <= len(relic_locations[relic]['vault']) and cycles:
                    relic_locations[relic]['cycles'].append(cycles)
                    cycles = 0

    return relic_locations


async def availability_manager(relics):

    relic_locations = get_availability_dict(relics)
    # print(relic_locations['Lith M7'])
    embed_info = {}

    for relic in relic_locations:
        if relic not in embed_info:
            embed_info[relic] = []
        if relic_locations[relic]['cycles']:
            for start, end, cycles, _type, av in \
                    zip(relic_locations[relic]['release'], relic_locations[relic]['vault'], relic_locations[relic]['cycles'], relic_locations[relic]['type'], relic_locations[relic]['available']):
                embed_info[relic].append({
                    'date_start': get_datetime(full_sheet[start][EVENT].split(': ')[0]),
                    'date_end': get_datetime(full_sheet[end][EVENT].split(': ')[0], av),
                    'event_start': full_sheet[start][EVENT].split(': ')[1],
                    'event_end': full_sheet[end][EVENT].split(': ')[1] if not av else 'Currently Available',
                    'pa_cycles': cycles if cycles else 0,
                    'available': av,
                    'type': _type
                })
        else:
            for start, end, _type, av in zip(relic_locations[relic]['release'], relic_locations[relic]['vault'], relic_locations[relic]['type'], relic_locations[relic]['available']):
                embed_info[relic].append({
                    'date_start': get_datetime(full_sheet[start][EVENT].split(': ')[0]),
                    'date_end': get_datetime(full_sheet[end][EVENT].split(': ')[0], av),
                    'event_start': full_sheet[start][EVENT].split(': ')[1],
                    'event_end': full_sheet[end][EVENT].split(': ')[1] if not av else 'Currently Available',
                    'pa_cycles': 0,
                    'available': av,
                    'type': _type
                })

    # embed_info = {k: embed_info[k] for k in sorted(list(embed_info))}
    embed_info = {k: v for k, v in sorted(embed_info.items(), key=lambda item: item[1][0]['date_start'])}

    av_embed = create_av_embed(embed_info)
    create_av_graph(embed_info)

    return av_embed


def get_datetime(date_str, av=False):

    if not av:
        date_str = date_str.replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' ')

    else:
        date_str = datetime.datetime.now().strftime('%B %d %Y')

    return datetime.datetime.strptime(date_str, '%B %d %Y')

def trim_event(event_str, _type):

    event_str = event_str.replace('\n', '').replace('Out:', '').replace('In:', '')
    event_str = event_str.replace(' Release,', ' 🆕\n').replace(' Vault', ' 🟥')

    if 'Regular' in _type and 'End,' in event_str:
        event_str = event_str.replace(' End,', ' End\n')

    if 'Unvault' in _type or ' End' in event_str or ' Start' in event_str:
        event_str = event_str.replace(' and ', ' / ').replace('Unvault ', '').replace(' Start', ' ✅').replace(' End,', ' 🟥\n').replace(' End', ' 🟥').replace('In:', '')


    return event_str


def create_av_graph(embed_info):

    dates = SCHARTS_DATES.copy()
    values = SCHARTS_VALUES.copy()
    averages = SCHARTS_AVERAGE.copy()
    values_sorted = sorted(values)
    val_dif = int(values_sorted[-1] - values_sorted[0])
    total = len(embed_info)

    relic_colors = {}

    fig = plt.figure(figsize=(12, 6), dpi=160)
    fig.suptitle(f"{', '.join(list(set(list(embed_info))))} Availability", fontsize=16)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(dates, values)
    ax.plot(dates, averages, color='green')
    ax.set_yticks(avg_ticks := [values_sorted[0] + x for x in range(0, val_dif, int(val_dif/10))])
    ax.set_yticklabels([f"{round(x / 1000, 1)}k" for x in avg_ticks])

    for i, relic in enumerate(embed_info):
        for relic_sub in embed_info[relic]:
            dupe = False
            if relic not in ['Neo O1', 'Axi V8', 'Axi A2', 'Axi A5']:
                if relic not in relic_colors:
                    relic_colors[relic] = COLORS[i]
                else:
                    dupe = True

                ax.axvspan(relic_sub['date_start'], relic_sub['date_end'], color=relic_colors[relic], alpha=0.5, label=('_' * dupe) + relic, ymax=(total-i)/total, ymin=(total-i-1)/total)

                if (date_range := relic_sub['date_end'] - relic_sub['date_start']).days > (dates[-1] - dates[0]).days / 32:

                    middle_x = date_range / 2 + relic_sub['date_start']
                    y_multiplier = ((((total-i)/total - (total-i-1)/total) / 2) + (total-i-1)/total)
                    middle_y = y_multiplier * (values_sorted[-1] - values_sorted[0]) + values_sorted[0]

                    ax.text(middle_x, middle_y, relic, ha='center', size='xx-small')

    # Conversion Span
    plt.axvline(datetime.datetime(2016,7,8), color='red', ls='--')
    plt.text(datetime.datetime(2016,7,8) - datetime.timedelta(days=30), 1.02, 'Conversion', transform=ax.get_xaxis_transform(), rotation=0)

    # Resurgence 1 Span
    plt.axvline(datetime.datetime(2021, 11, 16), color='red', ls='--', alpha=0.6)
    plt.axvline(datetime.datetime(2022, 1, 25), color='red', ls='--', alpha=0.6)
    plt.axvspan(datetime.datetime(2021, 11, 16), datetime.datetime(2022, 1, 25),
                ec='red', color='red', alpha=0.15, ls='--')
    plt.text(datetime.datetime(2021, 11, 16) - datetime.timedelta(days=30), 1.02, 'Resurgence', transform=ax.get_xaxis_transform(), rotation=0)

    # Conversion 2 Span
    plt.axvline(datetime.datetime(2023, 12, 21), color='red', ls='--', alpha=0.6)
    plt.axvline(datetime.datetime(2024, 2, 15), color='red', ls='--', alpha=0.6)
    plt.axvspan(datetime.datetime(2023, 12, 21), datetime.datetime(2024, 2, 15),
                ec='red', color='red', alpha=0.15, ls='--')
    plt.text(datetime.datetime(2023, 12, 21) - datetime.timedelta(days=30), 1.02, 'Resurgence', transform=ax.get_xaxis_transform(), rotation=0)

    plt.legend()
    fig.tight_layout()
    plt.margins(x=0.002)

    if relic_colors:
        plt.savefig('./data/plot_image.png', bbox_inches='tight', pad_inches=0.05)


def create_av_embed(embed_info):

    av_embed = discord.Embed(
                             title='Relic Availability',
                             description=f"Relics: {', '.join(list(embed_info))}"
    )

    row_counter = 0
    last_dupe = 0
    for relic in embed_info:
        dupe_counter = 0
        for data in embed_info[relic]:
            dupe_counter += 1
            row_counter += 1

            if last_dupe > 1 and dupe_counter < last_dupe and (row_counter - 1) % 3:
                for i in range(3 - ((row_counter - 1) % 3)):
                    av_embed.add_field(
                        name='\u200b',
                        value='\u200b',
                        inline=True
                    )
                    row_counter += 1
            last_dupe = dupe_counter

            av_embed.add_field(
                name=f"{relic} {data['type'] if 'Resurgence' not in data['type'] else 'Resurgence'}",
                value=  # f"{data['date_start'].strftime('%b %d %Y')} - {data['date_end'].strftime('%b %d %Y')}\n"
                      f"{(data['date_end'] - data['date_start']).days} Days{'  |  ' + str(data['pa_cycles']) + ' PA' if data['pa_cycles'] else '' + 's' if data['pa_cycles'] > 1 else ''}\n"
                      f"**FROM:**\n"
                      # f"{data['date_start'].strftime('%b %d, %Y')}\n"
                      f"<t:{int(data['date_start'].timestamp())}:D>\n"
                      f"{trim_event(data['event_start'], data['type'])}\n"
                      f"**TO:**\n"
                      # f"{data['date_end'].strftime('%b %d, %Y')}\n"
                      f"<t:{int(data['date_end'].timestamp())}:D>\n"
                      f"{trim_event(data['event_end'], data['type'])}",
                inline=True
            )

    return av_embed


def parse_vault_order(args):

    sets = [x.split(' Prime')[0] for x in list(get_set_data())]
    sets_str = '__'.join(sets)

    set_list = []
    temp_set = ''

    for arg in args:
        arg = arg.title()

        if arg in sets:
            set_list.append(arg)
        elif arg in sets_str:
            temp_set += f"{arg} "
            if temp_set.rstrip() in sets:
                set_list.append(temp_set.rstrip())
                temp_set = ''

    set_list = list(set(set_list))
    return set_list


def find_vault_order():

    today = datetime.datetime.now().strftime('%B %d %Y')
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    set_data = get_set_data()

    set_vault_date = {k.split(' Prime')[0]: tomorrow for k in list(set_data) if set_data[k]['type'] == 'Warframes'}
    frame_list = list(set_vault_date)

    active = {}

    for row in full_sheet[spreadsheet_ranges['relics'][0]:spreadsheet_ranges['relics'][1]]:
        if datetime.datetime.strptime(row[EVENT].split(': ')[0].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' '), '%B %d %Y') > datetime.datetime.now():
            break
        temp_vaulted = {}
        release_index = 0
        vault_index = 0
        start_index = 0
        end_index = 0
        in_index = 0
        out_index = 0
        for i, word in enumerate(row[EVENT].split()):
            word = word.replace('(', '').replace(')', '').replace(',', '')
            if word in frame_list:
                temp_vaulted[word] = i
            if 'Start' in word:
                start_index = i
            if 'Release' in word:
                release_index = i
            if 'End' in word:
                end_index = i
            if 'Vault' in word:
                vault_index = i
            if 'In:' in word:
                in_index = i
            if 'Out:' in word:
                out_index = i
            if 'Resurgence' in word:
                resurgence = True

        for frame, index in temp_vaulted.items():

            if index < end_index or release_index < index < vault_index or (out_index < index and out_index):
                set_vault_date[frame] = datetime.datetime.strptime(row[EVENT].split(': ')[0].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' '), '%B %d %Y')
                if frame in active:
                    active.pop(frame)
            if end_index < index < start_index or ((in_index < index and in_index) and (in_index < index < out_index if out_index else True)):
                set_vault_date[frame] = tomorrow
                if frame not in active:
                    active[frame] = datetime.datetime.strptime(row[EVENT].split(': ')[0].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' '), '%B %d %Y')

    date_set_vault = {}
    for k, v in set_vault_date.items():
        v = v.strftime('%b %d %Y')
        if v not in date_set_vault:
            date_set_vault[v] = [k]
        else:
            date_set_vault[v].append(k)


    dates = list(date_set_vault)
    dates = [y.strftime('%b %d %Y') for y in sorted([datetime.datetime.strptime(x, '%b %d %Y') for x in dates])]

    date_set_vault = {x: date_set_vault[x] for x in dates}
    date_set_vault.pop(tomorrow.strftime('%b %d %Y'))

    return date_set_vault, active

def find_unvault_sets(args):

    unvault_sets = get_unvault_relic_sets()
    valid_unvaults = {}

    for frame in args:
        for unv in unvault_sets:
            if frame in unv:
                if frame not in valid_unvaults:
                    valid_unvaults[frame] = {
                        unv: unvault_sets[unv]
                    }
                elif unv not in valid_unvaults[frame]:
                    valid_unvaults[frame][unv] = unvault_sets[unv]

    return valid_unvaults


def is_related(relics):

    related_dict = {}

    relics = sorted(relics, key=sort_relics)

    availability_dict = get_availability_dict(relics)
    relic_list = list(availability_dict)

    # print(json.dumps(availability_dict, indent=4))

    for i, relic in enumerate(relic_list):
        related_dict[relic] = {
            'related': {},
            'date_ranges': {},
            'time_spans': {}
        }

    for i, relic in enumerate(relic_list):
        for j, relic2 in enumerate(relic_list[i+1:]):
            date_start = []
            date_end = []
            for rel in availability_dict[relic]['release']:
                for rel2 in availability_dict[relic2]['release']:
                    date_start.append(max(rel, rel2))
            for rel in availability_dict[relic]['vault']:
                for rel2 in availability_dict[relic2]['vault']:
                    date_end.append(min(rel, rel2))

            valid_ranges = []
            for start, end in zip(date_start, date_end):
                if start < end:
                    valid_ranges.append([start, end])

            related_dict[relic]['date_ranges'][relic2] = valid_ranges
            related_dict[relic2]['date_ranges'][relic] = valid_ranges

            related_dict[relic]['related'][relic2] = bool(valid_ranges)
            related_dict[relic2]['related'][relic] = bool(valid_ranges)

            timespans = []
            for r in valid_ranges:
                start = get_datetime(full_sheet[r[0]][EVENT].split(': ')[0])
                end = get_datetime(full_sheet[r[1]][EVENT].split(': ')[0])
                if start < end:
                    timespans.append((end - start).days)

            timespans = sum(timespans)

            related_dict[relic]['time_spans'][relic2] = timespans
            related_dict[relic2]['time_spans'][relic] = timespans

    # print(related_dict)
    return related_dict


def related_sort_manager(flags):

    availability_dict = get_availability_dict(flags['relics'])
    target_relic = flags['relics'][0]
    all_relics, relics_detailed = get_all_relics_dict(availability_dict[target_relic]['release'], availability_dict[target_relic]['vault'], target_relic, flags)
    related_relics_time, related_relics_sets, related_relics_price, related_relics_event, related_relics_links = None, None, None, None, None

    if flags['links']:
        related_relics_links = related_sorted_price(all_relics, links=True)
        related_relics_links = related_links(related_relics_links, flags)

    elif flags['sort_style'] == 'Time':
        related_relics_time = related_sorted_time(relics_detailed)

    elif flags['sort_style'] == 'Sets':
        related_relics_sets = related_sorted_sets(all_relics)

    elif flags['sort_style'] == 'Price':
        related_relics_price = related_sorted_price(all_relics)

    elif flags['sort_style'] == 'Event':
        related_relics_event = None

    return related_relics_time, related_relics_sets, related_relics_price, related_relics_event, related_relics_links


def related_sorted_time(relics_detailed):

    related_relics = get_all_relics_over_time_period(relics_detailed)

    return related_relics


def related_sorted_sets(all_relics):

    set_sorted_related_relics = {}

    for relic in all_relics:
        for _set in get_sets_in_relic(relic):
            if _set not in set_sorted_related_relics:
                set_sorted_related_relics[_set] = []
            set_sorted_related_relics[_set].append(relic)

    return set_sorted_related_relics


def related_sorted_price(all_relics, links=False):

    price_sorted_related_relics = {}

    for relic in all_relics:

        relic_avg = get_relic_4b4_avg(relic)

        if relic_avg not in price_sorted_related_relics:
            price_sorted_related_relics[relic_avg] = []
        price_sorted_related_relics[relic_avg].append(relic)

    prices_sorted = sorted(list(price_sorted_related_relics), reverse=(not links))
    price_sorted_related_relics = {k: sorted(price_sorted_related_relics[k], key=sort_relics) for k in prices_sorted}

    return price_sorted_related_relics


def related_links(price_sorted_related_relics, flags):

    link_strs_list = ['']
    adj_price_sorted_relics = {}

    for price in price_sorted_related_relics:
        adj_price = int(price / flags['threshold_increment'])
        if adj_price not in adj_price_sorted_relics:
            adj_price_sorted_relics[adj_price] = []
        adj_price_sorted_relics[adj_price] += price_sorted_related_relics[price]

    for price in adj_price_sorted_relics:
        adj_price_sorted_relics[price] = sorted(adj_price_sorted_relics[price], key=sort_relics)

    priced = False
    for price, relics in adj_price_sorted_relics.items():
        for relic in relics:
            if len(link_strs_list[-1]) >= 200:
                if not priced:
                    link_strs_list[-1] += f" {price + flags['price_threshold']}p each"
                link_strs_list.append('')
            link_strs_list[-1] += f"{' ' * bool(link_strs_list[-1])}[{relic} Relic]"
            if relic == relics[-1]:
                link_strs_list[-1] += f" {price + flags['price_threshold']}p each"
                priced = True
            else:
                priced = False

    return link_strs_list


def get_sets_in_relic(relic):

    return [x.split(' Prime')[0] for x in get_relic_data()[relic]['Intact']['drops']
            if (x not in "Forma Blueprint" and x.split(' Prime')[0] not in get_prime_junk())]


def get_all_relics_dict(start, end, relic, flags):
    relics_detailed = {}
    all_relics = []
    for s, e in zip(start, end):
        relics = []
        relics_detailed[f"{s}-{e}"] = dict()
        for row in full_sheet[s:e]:
            relics += row[TOTAL_RELICS].split(', ')
        relics_to_remove = [rel for rel in full_sheet[e][RELICS_IN].split(', ')] + [relic]
        relics = [rel for rel in relics if rel not in relics_to_remove]

        relics = sorted(list(set(relics)), key=sort_relics)
        relics = format_relic_list(relics, flags)
        all_relics += relics

        relics_detailed[f"{s}-{e}"] = get_availability_dict(relics)

    return sorted(list(set(all_relics)), key=sort_relics), relics_detailed


def get_all_relics_over_time_period(relics_detailed):

    relics_sorted_time_available = {
        'totals': {}
    }
    for time in relics_detailed:
        relics_sorted_time_available[time] = {}
        for k, v in relics_detailed[time].items():
            _start = []
            _end = []
            _diff = 0

            for _s, _e, _a in zip(v['release'], v['vault'], v['available']):

                if (int(time.split('-')[0]) >= _s and int(time.split('-')[1]) <= _e) or \
                        int(time.split('-')[0]) <= _e <= int(time.split('-')[1]) or \
                        int(time.split('-')[0]) <= _s <= int(time.split('-')[1]):

                    if _s < int(time.split('-')[0]):
                        _s = int(time.split('-')[0])
                    if _e > int(time.split('-')[1]):
                        _e = int(time.split('-')[1])

                    _start.append(get_datetime(full_sheet[_s][EVENT].split(': ')[0]))
                    _end.append(get_datetime(full_sheet[_e][EVENT].split(': ')[0]))
                    _diff += (_end[-1] - _start[-1]).days


            if _diff > 0:
                if k not in relics_sorted_time_available['totals']:
                    relics_sorted_time_available['totals'][k] = 0
                relics_sorted_time_available['totals'][k] += _diff
                if _diff not in relics_sorted_time_available[time]:
                    relics_sorted_time_available[time][_diff] = []
                relics_sorted_time_available[time][_diff].append(k)

    if 'totals' in relics_sorted_time_available:
        relics_sorted_time_available['totals'] = {k: v for k, v in sorted(relics_sorted_time_available['totals'].items(), key=lambda item: item[1], reverse=True)}

    for _time in relics_sorted_time_available:
        if _time != 'totals':
            sorted_keys = sorted(list(relics_sorted_time_available[_time]), reverse=True)
            sorted_dict = {k: relics_sorted_time_available[_time][k] for k in sorted_keys}
            relics_sorted_time_available[_time] = sorted_dict

    # print(relics_sorted_time_available)

    # ALL TIMES ARE DONE, NEED TO DO FRONT-END NOW

    return relics_sorted_time_available


def format_relic_list(relics, flags):
    formatted_relics = []

    for relic in relics:
        if flags['average_return'] < get_relic_data()[relic][get_best_refinement(relic)]['average_return']['4b4'] and \
           flags['junk_amount'] > get_junk_amount(relic) and \
           (check_unvault(relic) if flags['return_unvault'] else True) and \
           (check_rarest(relic) if flags['rarest_only'] else True) and \
           (check_sets(relic, flags['sets']) if flags['sets'] else True):
            formatted_relics.append(relic)

    return formatted_relics


def get_best_refinement(relic):

    relic_data = get_relic_data()[relic]
    best_style = 'Radiant'
    best_price = 0
    for ref in relic_data:
        if (new_price := relic_data[ref]['average_return']['4b4']) > best_price:
            best_price = new_price
            best_style = ref

    return best_style


def get_junk_amount(relic):

    relic_data = get_relic_data()[relic]
    total_junk = 0
    for part in relic_data['Intact']['drops']:
        if part.split()[0] in get_prime_junk() or part.split()[0] in 'Forma Blueprint':
            total_junk += 1

    return total_junk


def check_unvault(relic):
    unvaults = get_unvault_relic_sets()

    for unvault in unvaults:
        if relic in unvaults[unvault]:
            return True

    return False


def check_rarest(relic):
    return f"{relic} RELIC".upper() in get_rarest_relics()


def check_sets(relic, sets):

    for part in get_relic_data()[relic]['Intact']['drops']:
        if part.title().split(' Prime')[0] in sets:
            return True

    return False


def get_overlapping_relics(relics):

    all_relics = []

    for relic in relics:
        for row in full_sheet[spreadsheet_ranges['relics'][0]:spreadsheet_ranges['relics'][1]]:
            if relic in row[TOTAL_RELICS]:
                for rel in row[TOTAL_RELICS].split(', '):
                    if rel not in all_relics:
                        all_relics.append(rel)

    return all_relics


def get_vault_date_order():
    vault_dict = get_vault_dates()

    embed = discord.Embed(
        title='Frames in order of vault',
        description='Data not updated, check the bottom of:\n[Relic Spreadsheet](https://docs.google.com/spreadsheets/d/1lHt3CaaCEdNR1ZSH8BaWFERMFHnxSkpGxQV4R_CiSyI/edit?usp=sharing)'
    )

    frame_str, date_str, timestamp_str = '', '', ''
    present_bool = False
    for frame, date in vault_dict.items():
        present_bool = present_bool or ('--present' in frame)

        frame_str += f"{frame}\n" * ('--present' not in frame) + '\n**Not Vaulted**\n' * ('--present' in frame)

        if not present_bool:
            date_stamp = f"<t:{int((datetime.datetime.strptime(date.replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' '), '%B %d %Y') + datetime.timedelta(hours=14)).timestamp())}:R>\n"
        else:
            try:
                date_stamp = f"<t:{int((datetime.datetime.strptime(date, '%B %d %Y') + datetime.timedelta(hours=14)).timestamp())}:R>\n"
            except ValueError:
                date_stamp = '\n**Approx Vault Date**'

        timestamp_str += date_stamp * ('--present' not in frame) + '\n**Approx Vault Date**\n' * ('--present' in frame)

    embed.add_field(
        name='Frame',
        value=frame_str
    )
    embed.add_field(
        name='Vaulted',
        value=timestamp_str
    )

    return embed


async def auto_update_vault_date_order():
    # vault_dict = get_vault_dates()
    vault_dict = {}
    release_dict = {}
    sheet_range = full_sheet[spreadsheet_ranges['relics'][0]:spreadsheet_ranges['relics'][1]]

    time_between_vaults_total = 0
    last_date = sheet_range[0][1].split(': ')[0].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' ')
    last_date = datetime.datetime.strptime(last_date, "%B %d %Y")

    for cell in [c[1] for c in sheet_range]:
        if ' Vault' in cell:
            frame = cell.split(' Vault')[0].split(' ')[-1]
            date = cell.split(': ')[0]
            vault_dict[frame] = date

            date = date.replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' ')
            date = datetime.datetime.strptime(date, "%B %d %Y")
            time_between_vaults_total += (date - last_date).days
            last_date = date

        if ' Release' in cell:
            frame = cell.split(' Release')[0].split(' ')[-1]
            date = cell.split(': ')[0]
            release_dict[frame] = date

    release_dict = {k: v for k, v in release_dict.items() if k not in vault_dict}

    total_amount_vaulted = len(vault_dict)
    average_time_between_vaults = int(time_between_vaults_total/total_amount_vaulted)

    for frame in release_dict:
        # date = release_dict[frame].replace('1st', '1').replace('2nd', '2').replace('3rd', '3').replace('th ', ' ')
        # date = datetime.datetime.strptime(date, "%B %d %Y")
        next_vault = last_date + relativedelta(days=average_time_between_vaults)
        release_dict[frame] = get_closest_weekday(next_vault, 3).strftime("%B %d %Y")
        last_date = next_vault

    vault_dict.update({'--present': '--'})
    vault_dict.update(release_dict)
    update_vault_dates(vault_dict)

def get_closest_weekday(date: datetime.datetime, weekday: int) -> datetime.datetime:

    days_until_weekday = weekday - date.weekday() % 7
    closest_weekday_date = date + datetime.timedelta(days=days_until_weekday)

    return closest_weekday_date
