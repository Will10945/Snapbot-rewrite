import json
import datetime
import os
import shutil

from lib.utils.file_utils import update_server_prefixes, get_server_prefixes, get_default_prefix, get_backup_params


def server_prefix_manager(guild_id, bot_id, content):

    prefixes = get_server_prefixes()
    default_prefix = get_default_prefix()

    if guild_id not in list(prefixes) and (default_prefix in content or f'<@!{bot_id}>' in content):
        prefixes[guild_id] = default_prefix
        update_server_prefixes(prefixes)
        return f'No prefix set, new prefix: `{default_prefix}`'

    elif f'<@!{bot_id}>' in content and guild_id in list(prefixes):
        if len(content.split(' ')) == 1:
            return f'The prefix for this server is: `{prefixes[guild_id]}`'


def backup_manager(force=False, shutdown=False):
    data_dir = f"./data"
    backup_dir = f"./backups"
    backup_date = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H')+ ('__forced' * force) + ('__shutdown' * shutdown)}"
    dir_append = ''

    if not os.path.exists(f"{backup_dir}/{backup_date}"):
        os.makedirs(f"{backup_dir}/{backup_date}")
        copy_files(data_dir, backup_dir, dir_append, backup_date)

    for file in os.listdir(f"{backup_dir}"):
        if datetime.datetime.strptime(file.split('__')[0], '%Y-%m-%d_%H') < datetime.datetime.now() - datetime.timedelta(hours=get_backup_params()['lifespan']):
            shutil.rmtree(f"{backup_dir}/{file}")



def copy_files(data_dir, backup_dir, dir_append, backup_date):

    if dir_append:
        if f"{dir_append}" not in os.listdir(f"{backup_dir}/{backup_date}"):
            # print(f"Creating directory {backup_dir}/{backup_date}/{dir_append}{'/' if dir_append else ''}")
            os.makedirs(f"{backup_dir}/{backup_date}/{dir_append}{'/' * bool(dir_append)}")

    for file in os.listdir(f"{data_dir}{'/' * bool(dir_append)}{dir_append}"):
        if os.path.isdir(new_dir := f"{data_dir}/{dir_append}{'/' * bool(dir_append)}{file}"):
            dir_append_new = new_dir.split(data_dir + '/')[1]
            copy_files(data_dir, backup_dir, dir_append_new, backup_date)
        else:
            # print(f"Backing up {data_dir}/{dir_append}{'/' if dir_append else ''}{file} TO {backup_dir}/{backup_date}/{dir_append}{'/' if dir_append else ''}{file}")
            shutil.copyfile(f"{data_dir}/{dir_append}{'/' * bool(dir_append)}{file}", f"{backup_dir}/{backup_date}/{dir_append}{'/' * bool(dir_append)}{file}")

