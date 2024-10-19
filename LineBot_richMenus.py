# from bot_config import LINEBOT_ACCESS_TOKEN
from config import LINEBOT_ACCESS_TOKEN

import requests
import json
import os
# import pyodbc
import pandas as pd
# from sqlalchemy import create_engine
# from bot_config import MSSQL_ENGINE, MSSQL_DRIVER
from linebot.models import *
from linebot import LineBotApi
import argparse
import warnings

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN)

# engine = create_engine(MSSQL_ENGINE)
# cnxn = pyodbc.connect(MSSQL_DRIVER)

# IMAGE_PATH = "./assets"
# F_HALF_RICHMENU_FILE = './assets/first_half_richmenu_id.txt'
# S_HALF_RICHMENU_FILE = './assets/second_half_richmenu_id.txt'
# ENG_RICHMENU_FILE = './assets/english_richmenu_id.txt'
# F_HALF_RICHMENU_FILE = './assets/first_half_richmenu_id.txt'
# S_HALF_RICHMENU_FILE = './assets/second_half_richmenu_id.txt'
# ENG_RICHMENU_FILE = './assets/english_richmenu_id.txt'

WIDTH = 1200
HEIGHT = 820

def set_first_half_semester_rich_menus():
    file = './data/menu.png'
    # create
    data = {
        "size": {
            "width": WIDTH,
            "height": HEIGHT,
        },
        "selected": True,
        "name": "選單",
        "chatBarText": "選單",
        "areas": [
            { # showPrizes
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": WIDTH/2,
                    "height": HEIGHT/2
                },
                "action": {
                    "type": "postback",
                    "data": "showPrizes"
                }
            },
            { # myPoints
                "bounds": {
                    "x": WIDTH/2,
                    "y": 0,
                    "width": WIDTH/2,
                    "height": HEIGHT/2
                },
                "action": {
                    "type": "postback",
                    "data": "myPoints"
                }
            },
            { # myPrize
                "bounds": {
                    "x": 0,
                    "y": HEIGHT/2,
                    "width": WIDTH/2,
                    "height": HEIGHT/2
                },
                "action": {
                    "type": "postback",
                    "data": "myPrize"
                }
            },
            { # website
                "bounds": {
                    "x": WIDTH/2,
                    "y": HEIGHT/2,
                    "width": WIDTH/2,
                    "height": HEIGHT/2
                },
                "action": {
                    "type": "uri",
                    "label": "website",
                    # 學校網頁改版 the link no longer redirects to calendar
                    # "uri": "https://www.nycu.edu.tw/calendar/"
                    "uri": "http://140.112.251.50:3000",
                }
            }
        ]
    }
    richmenu_id = create(data)
    # 上傳圖片
    upload_image(file, richmenu_id)
    # set alias
    # set_alias(richmenu_id, "campus_life")
    # 記錄下來 之後要link to user用
    # with open(F_HALF_RICHMENU_FILE, 'w') as f:
    #     f.write(f'{richmenu_id}\n')
    return richmenu_id

def create(data):
    create_url = "https://api.line.me/v2/bot/richmenu"
    headers = {
        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = json.dumps(data, indent=2)
    richmenu_id = requests.post(create_url, data, headers=headers)
    print(f"create {richmenu_id.json()}")
    richmenu_id = json.loads(richmenu_id.text)['richMenuId']    
    return richmenu_id


def set_default(richmenu_id):
    set_default_url = f"https://api.line.me/v2/bot/user/all/richmenu/{richmenu_id}"
    res = requests.post(set_default_url, headers={
                        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}'})
    print(f"set_default {res}")


def upload_image(file, richmenu_id):
    # 上傳圖片
    api = f'https://api-data.line.me/v2/bot/richmenu/{richmenu_id}/content'
    with open(os.path.join(file), 'rb') as image:
        headers = {
            'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}',
            'Content-Type': 'image/png'
        }
        response = requests.post(api, data=image, headers=headers)
        print(f"upload_image {response}")
        print(response.json())


def set_alias(richmenu_id, alias):
    api = "https://api.line.me/v2/bot/richmenu/alias"
    headers = {
        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "richMenuAliasId": alias,
        "richMenuId": richmenu_id
    }
    data = json.dumps(data, indent=2)
    res = requests.post(api, data, headers=headers)
    print(f"set_alias {res}")


def get_rich_menus():
    get_url = "https://api.line.me/v2/bot/richmenu/list"
    headers = {
        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}',
    }
    response = requests.get(get_url, headers=headers)
    return json.loads(response.text)


def get_alias():
    get_url = "https://api.line.me/v2/bot/richmenu/alias/list"
    headers = {
        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}',
    }
    response = requests.get(get_url, headers=headers)
    return json.loads(response.text)


def delete_all():
    rich_menu_dict = get_rich_menus()
    headers = {
        'Authorization': f'Bearer {LINEBOT_ACCESS_TOKEN}'
    }
    for rich_menu in rich_menu_dict["richmenus"]:
        del_url = f"https://api.line.me/v2/bot/richmenu/{rich_menu['richMenuId']}"
        res = requests.delete(del_url, headers=headers)
        print(f"delet_all-richmenu {res}")

    alias_dict = get_alias()
    for alias in alias_dict["aliases"]:
        del_url = f"https://api.line.me/v2/bot/richmenu/alias/{alias['richMenuAliasId']}"
        res = requests.delete(del_url, headers=headers)
        print(f"delet_all-alias {res}")


def link_richmenu_to_user(file, user_id):
    try:
        with open(file, 'r') as file:
            richmenu_id = file.readline()
            richmenu_id = richmenu_id.strip()
            url = f'https://api.line.me/v2/bot/user/{user_id}/richmenu/{richmenu_id}'
            headers = {"Authorization": f"Bearer {LINEBOT_ACCESS_TOKEN}"}
            res = requests.post(url, headers=headers)
            print(res.text)
    except Exception as err:
        print(err)
        raise Exception
    
def link_richmenu_to_multiple_users():
    try:
        richmenu_id = set_first_half_semester_rich_menus()
        print(type(richmenu_id))
        print(richmenu_id)
        richmenu_id = richmenu_id.strip()
        url = f'https://api.line.me/v2/bot/richmenu/bulk/link'
        headers = {"Authorization": f"Bearer {LINEBOT_ACCESS_TOKEN}", "Content-Type": "application/json"}
        
        with open('data/userStatus.json', 'r') as file:
            userStatus = json.load(file)
            user_ids_list = list(userStatus.keys())
        data = {
            "richMenuId": richmenu_id,
            "userIds": user_ids_list
        }
        data = json.dumps(data, indent=2)
        res = requests.post(url, headers=headers, data=data)
        if res.status_code != 202:
            print(res.text)
    except Exception as err:
        print(err)
        raise Exception

if __name__ == "__main__":
    link_richmenu_to_multiple_users()
