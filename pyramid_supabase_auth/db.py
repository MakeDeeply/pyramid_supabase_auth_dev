'''
Python supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
import os
import sys
from supabase.client import create_client, Client, ClientOptions

# conventional approach ... if it works
# url = os.environ.get('SUPABASE_URL')
# key = os.environ.get('SUPABASE_KEY')

# workaround some path issues:
script_folder = os.path.dirname(os.path.abspath(__file__))
if script_folder not in sys.path:
    sys.path.append(script_folder)

import local_settings  # should NOT be stored in git


url: str = local_settings.settings.get('SUPABASE_URL')
key: str = local_settings.settings.get('SUPABASE_KEY')

# used below and imported elsewhere
supabase: Client = create_client(url, key, options=ClientOptions(flow_type='pkce'))

supabase.auth._start_auto_refresh_token(value=3600)

# used by multiple scripts
colors = [  # RGB, CMYK, white
    'red',
    'green',
    'blue',

    'cyan',
    'magenta',
    'yellow',
    'black',

    'white',
]


def get_user_color(id):
    try:
        return (
            supabase.table('Color')
            .select('user_id, favourite_color')  # favour / favor
            .filter('user_id', 'eq', str(id))
            .execute()
            .data[0]['favourite_color']
        )
    except: # user hasn't set their favourite color yet
        return None


def get_all_users_colors():
    try:
        return (
            supabase.table('Color')
            .select('user_id, favourite_color')  # favour / favor
            .execute()
            .data
        )
    except: # no users
        return []


def get_users():
    try:
        return supabase.auth.admin.list_users()
    except:  # no users
        return []


def set_user_color(id, color):
    try:
        return (
            supabase.table('Color')
            .upsert(
                {
                    'user_id': id,
                    'favourite_color': color,
                }
            )
            .execute()
            .data
        )
    except Exception as e:
        print('ERROR in set_user_color', e)
        return None
