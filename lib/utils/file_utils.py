import json
import copy


# BOT_DATA
with open('./data/bot_data.json') as f:
    bot_data = json.load(f)

def update_bot_data():
    with open('./data/bot_data.json', 'w') as f0:
        json.dump(bot_data, f0, indent=4)

def get_server_prefixes():
    return bot_data['server_prefixes']

def get_default_prefix():
    return bot_data['default_prefix']

def get_prime_access_list():
    return bot_data['prime_access']

def get_meta_sets():
    return bot_data['meta_sets']

def get_expanded_meta_sets():
    return bot_data['expanded_meta_sets']

def get_prime_junk():
    return bot_data['prime_junk']

def get_relic_numbers():
    return bot_data['relic_numbers']

def get_last_price_update():
    return bot_data['last_price_update']

def get_dad_users():
    return bot_data['dad_users']

def get_tags():
    return bot_data['tags']

def get_baro_time():
    return bot_data['baro_time']

def get_trade_data():
    return bot_data['trade_data']

def get_rarest_relics():
    return bot_data['rarest_relics']

def get_almost_rarest_relics():
    return bot_data['almost_rarest_relics']

def get_unvault_relic_sets():
    return bot_data['unvault_relic_sets']

def get_backup_params():
    return bot_data['backup_params']

def update_server_prefixes(arg):
    bot_data['server_prefixes'] = arg
    update_bot_data()

def update_backup_params(arg):
    bot_data['backup_params'] = arg
    update_bot_data()

def update_prime_access_dict(arg):
    bot_data['prime_access'] = arg
    update_bot_data()

def update_relic_numbers(arg):
    bot_data['relic_numbers'] = arg
    update_bot_data()

def update_unvault_relic_sets(arg):
    bot_data['unvault_relic_sets'] = arg
    update_bot_data()


# RELIC_DATA
with open('./data/relic_data.json') as f:
    relic_data = json.load(f)

def update_relic_data():
    with open('./data/relic_data.json', 'w') as f0:
        json.dump(relic_data, f0, indent=4)

def get_relic_data():
    return relic_data

def new_relic_data(new_data):
    global relic_data
    relic_data = new_data
    update_relic_data()


# SET_DATA
with open('./data/set_data.json') as f:
    set_data = json.load(f)

def update_set_data():
    with open('./data/set_data.json', 'w') as f0:
        json.dump(set_data, f0, indent=4)

def get_set_data():
    return set_data

def new_set_data(new_data):
    global set_data
    set_data = new_data
    update_set_data()


# GEN_RELIC_DATA
with open('./data/gen_relic_data/gen_relic_filepaths.json') as f:
    gen_relic_filepaths = json.load(f)

def get_gen_relic_filepaths():
    return gen_relic_filepaths


with open(f"{get_gen_relic_filepaths()['generated_relics_data']}") as f:
    gen_relics_data = json.load(f)

def get_gen_relics_data():
    return gen_relics_data

def new_gen_relics_data(new_data):
    global gen_relics_data
    gen_relics_data = new_data
    update_gen_relics_data()

def update_gen_relics_data():
    with open(f"{get_gen_relic_filepaths()['generated_relics_data']}", 'w') as f0:
        json.dump(gen_relics_data, f0, indent=4)


# GEN_RELICS
with open(f"{get_gen_relic_filepaths()['generated_relics']}") as f:
    gen_relics = json.load(f)

def get_gen_relics():
    return gen_relics

def new_gen_relics(new_relics):
    global gen_relics
    gen_relics = new_relics
    update_gen_relics()

def update_gen_relics():
    with open(f"{get_gen_relic_filepaths()['generated_relics']}", 'w') as f0:
        json.dump(gen_relics, f0, indent=4)


# RELATED_RELICS
with open('./data/related_user_defaults.json') as f:
    related_user_defaults = json.load(f)

def get_related_user_defaults():
    return related_user_defaults

def update_related_user_defaults(new_data):
    global related_user_defaults
    related_user_defaults = new_data
    with open('./data/related_user_defaults.json', 'w') as f0:
        json.dump(gen_relics, f0, indent=4)
