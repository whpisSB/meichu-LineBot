from bot_config import LINE_CHANNEL_ACCESS_TOKEN
import requests
import json
import os
import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from bot_config import MSSQL_ENGINE, MSSQL_DRIVER
from linebot.models import *
from linebot import LineBotApi
import argparse
import warnings

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

engine = create_engine(MSSQL_ENGINE)
cnxn = pyodbc.connect(MSSQL_DRIVER)

IMAGE_PATH = "./assets"
F_HALF_RICHMENU_FILE = './assets/first_half_richmenu_id.txt'
S_HALF_RICHMENU_FILE = './assets/second_half_richmenu_id.txt'
ENG_RICHMENU_FILE = './assets/english_richmenu_id.txt'
F_HALF_RICHMENU_FILE = './assets/first_half_richmenu_id.txt'
S_HALF_RICHMENU_FILE = './assets/second_half_richmenu_id.txt'
ENG_RICHMENU_FILE = './assets/english_richmenu_id.txt'


def set_first_half_semester_rich_menus():
    for file in os.listdir(IMAGE_PATH):
        if file == "多層圖文選單_A.png":
            # create
            data = {
                "size": {
                    "width": 1625,
                    "height": 1083
                },
                "selected": True,
                "name": "校園生活",
                "chatBarText": "查看更多資訊",
                "areas": [
                    {
                        "bounds": {
                            "x": 539,
                            "y": 0,
                            "width": 549,
                            "height": 123
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "school_info",
                            "data": "校園生活換到教務資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1079,
                            "y": 0,
                            "width": 543,
                            "height": 120
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "freshman",
                            "data": "校園生活換到新生專區"
                        }
                    },
                    {
                        "bounds": {
                            "x": 12,
                            "y": 33,
                            "width": 414,
                            "height": 424
                        },
                        "action": {
                            "type": "uri",
                            "label": "行事曆",
                            # 學校網頁改版 the link no longer redirects to calendar
                            # "uri": "https://www.nycu.edu.tw/calendar/"
                            "uri": "https://www.nycu.edu.tw/nycu/ch/app/artwebsite/view?module=artwebsite&id=476&serno=49696c0f-84e8-4b92-8d34-a43a32e8d642",
                        }
                    },
                    {
                        "bounds": {
                            "x": 437,
                            "y": 133,
                            "width": 345,
                            "height": 451
                        },
                        "action": {
                            "type": "message",
                            "label": "交通資訊",
                            "text": "@交通資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 790,
                            "y": 161,
                            "width": 419,
                            "height": 405
                        },
                        "action": {
                            "type": "message",
                            "label": "學餐資訊",
                            "text": "@學餐資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1213,
                            "y": 165,
                            "width": 392,
                            "height": 419
                        },
                        "action": {
                            "type": "message",
                            "label": "緊急聯絡電話",
                            "text": "@緊急聯絡電話"
                        }
                    },
                    {
                        "bounds": {
                            "x": 29,
                            "y": 658,
                            "width": 382,
                            "height": 382
                        },
                        "action": {
                            "type": "message",
                            "label": "近期活動",
                            "text": "@近期活動"
                        }
                    },
                    {
                        "bounds": {
                            "x": 833,
                            "y": 695,
                            "width": 358,
                            "height": 344
                        },
                        "action": {
                            "type": "message",
                            "label": "位置資訊",
                            "text": "@位置資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1202,
                            "y": 705,
                            "width": 407,
                            "height": 368
                        },
                        "action": {
                            "type": "message",
                            "label": "常見Q&A",
                            "text": "@常見Q&A"
                        }
                    },
                    {
                        "bounds": {
                            "x": 436,
                            "y": 683,
                            "width": 394,
                            "height": 397
                        },
                        "action": {
                            "type": "message",
                            "label": "場館營業時間",
                            "text": "@場館營業時間"
                        }
                    },

                ]
            }
            richmenu_id = create(data)
            # 上傳圖片
            upload_image(file, richmenu_id)
            # set alias
            set_alias(richmenu_id, "campus_life")
            # 記錄下來 之後要link to user用
            with open(F_HALF_RICHMENU_FILE, 'w') as f:
                f.write(f'{richmenu_id}\n')
        if file == "多層圖文選單_B.png":
            # create
            data = {
                "size": {
                    "width": 1625,
                    "height": 1083
                },
                "selected": False,
                "name": "教務資訊",
                "chatBarText": "查看更多資訊",
                "areas": [
                    {
                        "bounds": {
                            "x": 0,
                            "y": 0,
                            "width": 555,
                            "height": 494
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "campus_life",
                            "data": "教務資訊換到校園生活"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1079,
                            "y": 0,
                            "width": 543,
                            "height": 120
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "freshman",
                            "data": "教務資訊換到新生專區"
                        }
                    },
                    {
                        "bounds": {
                            "x": 25,
                            "y": 141,
                            "width": 493,
                            "height": 458
                        },
                        "action": {
                            "type": "message",
                            "label": "教務資訊",
                            "text": "@教務資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 555,
                            "y": 144,
                            "width": 507,
                            "height": 420
                        },
                        "action": {
                            "type": "message",
                            "label": "獎學金",
                            "text": "獎學金"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1106,
                            "y": 139,
                            "width": 513,
                            "height": 440
                        },
                        "action": {
                            "type": "message",
                            "label": "國際交換",
                            "text": "@國際交換"
                        }
                    },
                    {
                        "bounds": {
                            "x": 20,
                            "y": 593,
                            "width": 511,
                            "height": 459
                        },
                        "action": {
                            "type": "message",
                            "label": "工讀資訊",
                            "text": "@工讀資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 556,
                            "y": 610,
                            "width": 520,
                            "height": 444
                        },
                        "action": {
                            "type": "message",
                            "label": "SDGs",
                            "text": "@SDGs"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1115,
                            "y": 614,
                            "width": 499,
                            "height": 455
                        },
                        "action": {
                            "type": "message",
                            "label": "分享帳號",
                            "text": "@分享帳號"
                        }
                    },
                ]
            }
            richmenu_id = create(data)
            # 上傳圖片
            upload_image(file, richmenu_id)
            # set alias
            set_alias(richmenu_id, "school_info")
        if file == "多層圖文選單_C.png":
            # create
            data = {
                "size": {
                    "width": 1625,
                    "height": 1083
                },
                "selected": False,
                "name": "新生專區",
                "chatBarText": "查看更多資訊",
                "areas": [
                    {
                        "bounds": {
                            "x": 0,
                            "y": 0,
                            "width": 540,
                            "height": 120
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "school_live",
                            "data": "新生專區換到校園生活"
                        }
                    },
                    {
                        "bounds": {
                            "x": 539,
                            "y": 0,
                            "width": 543,
                            "height": 120
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "school_info",
                            "data": "新生專區換到教務資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 3,
                            "y": 123,
                            "width": 804,
                            "height": 470
                        },
                        "action": {
                            "type": "message",
                            "label": "帳號開通",
                            "text": "@帳號開通"
                        }
                    },
                    {
                        "bounds": {
                            "x": 813,
                            "y": 120,
                            "width": 808,
                            "height": 475
                        },
                        "action": {
                            "type": "message",
                            "label": "新生活動",
                            "text": "@新生活動"
                        }
                    },
                    {
                        "bounds": {
                            "x": 0,
                            "y": 604,
                            "width": 807,
                            "height": 476
                        },
                        "action": {
                            "type": "message",
                            "label": "學期選課",
                            "text": "@學期選課"
                        }
                    },
                    {
                        "bounds": {
                            "x": 813,
                            "y": 600,
                            "width": 807,
                            "height": 479
                        },
                        "action": {
                            "type": "message",
                            "label": "社團活動",
                            "text": "@社團活動"
                        }
                    }
                ]
            }
            richmenu_id = create(data)
            # 上傳圖片
            upload_image(file, richmenu_id)
            # set alias
            set_alias(richmenu_id, "freshman")

def set_second_half_semester_rich_menus():
    for file in os.listdir(IMAGE_PATH):
        if file == "多層選單下學期_A.png":
            # create
            data = {
                "size": {
                    "width": 1625,
                    "height": 1083
                },
                "selected": True,
                "name": "校園生活",
                "chatBarText": "查看更多資訊",
                "areas": [
                    {
                        "bounds": {
                            "x": 713,
                            "y": 0,
                            "width": 714,
                            "height": 130
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "second_school_info",
                            "data": "校園生活換到校務資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1426,
                            "y": 0,
                            "width": 199,
                            "height": 128
                        },
                        "action": {
                            "type": "postback",
                            "data": "to_english",
                        }
                    },
                    {
                        "bounds": {
                            "x": 52,
                            "y": 163,
                            "width": 358,
                            "height": 399
                        },
                        "action": {
                            "type": "uri",
                            "label": "行事曆",
                            # 學校網頁改版 the link no longer redirects to calendar
                            # "uri": "https://www.nycu.edu.tw/calendar/"
                            "uri": "https://www.nycu.edu.tw/nycu/ch/app/artwebsite/view?module=artwebsite&id=476&serno=49696c0f-84e8-4b92-8d34-a43a32e8d642",
                        }
                    },
                    {
                        "bounds": {
                            "x": 431,
                            "y": 177,
                            "width": 348,
                            "height": 380
                        },
                        "action": {
                            "type": "message",
                            "label": "交通資訊",
                            "text": "@交通資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 805,
                            "y": 175,
                            "width": 403,
                            "height": 415
                        },
                        "action": {
                            "type": "message",
                            "label": "學餐資訊",
                            "text": "@學餐資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1215,
                            "y": 177,
                            "width": 383,
                            "height": 405
                        },
                        "action": {
                            "type": "message",
                            "label": "緊急聯絡電話",
                            "text": "@緊急聯絡電話"
                        }
                    },
                    {
                        "bounds": {
                            "x": 7,
                            "y": 587,
                            "width": 411,
                            "height": 448
                        },
                        "action": {
                            "type": "message",
                            "label": "近期活動",
                            "text": "@近期活動"
                        }
                    },
                    {
                        "bounds": {
                            "x": 825,
                            "y": 585,
                            "width": 356,
                            "height": 470
                        },
                        "action": {
                            "type": "message",
                            "label": "位置資訊",
                            "text": "@位置資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1201,
                            "y": 581,
                            "width": 397,
                            "height": 479
                        },
                        "action": {
                            "type": "message",
                            "label": "校園安全SOP",
                            "text": "@校園安全SOP"
                        }
                    },
                    {
                        "bounds": {
                            "x": 429,
                            "y": 585,
                            "width": 387,
                            "height": 458
                        },
                        "action": {
                            "type": "message",
                            "label": "場館營業時間",
                            "text": "@場館營業時間"
                        }
                    },

                ]
            }
            richmenu_id = create(data)
            # 上傳圖片
            upload_image(file, richmenu_id)
            # set alias
            set_alias(richmenu_id, "second_campus_life")
            # 記錄下來 之後要link to user用
            with open(S_HALF_RICHMENU_FILE, 'w') as f:
                f.write(f'{richmenu_id}\n')
        if file == "多層選單下學期_B.png":
            # create
            data = {
                "size": {
                    "width": 1625,
                    "height": 1083
                },
                "selected": False,
                "name": "校務資訊",
                "chatBarText": "查看更多資訊",
                "areas": [
                    {
                        "bounds": {
                            "x": 0,
                            "y": 0,
                            "width": 715,
                            "height": 128
                        },
                        "action": {
                            "type": "richmenuswitch",
                            "richMenuAliasId": "second_campus_life",
                            "data": "校務資訊換到校園生活"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1426,
                            "y": 0,
                            "width": 204,
                            "height": 130
                        },
                        "action": {
                            "type": "postback",
                            "data": "to_english",
                        }
                    },
                    {
                        "bounds": {
                            "x": 25,
                            "y": 141,
                            "width": 507,
                            "height": 450
                        },
                        "action": {
                            "type": "message",
                            "label": "教務資訊",
                            "text": "@教務資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 540,
                            "y": 157,
                            "width": 547,
                            "height": 435
                        },
                        "action": {
                            "type": "message",
                            "label": "獎學金",
                            "text": "獎學金"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1106,
                            "y": 159,
                            "width": 503,
                            "height": 430
                        },
                        "action": {
                            "type": "message",
                            "label": "國際交換",
                            "text": "@國際交換"
                        }
                    },
                    {
                        "bounds": {
                            "x": 20,
                            "y": 608,
                            "width": 523,
                            "height": 441
                        },
                        "action": {
                            "type": "message",
                            "label": "工讀資訊",
                            "text": "@工讀資訊"
                        }
                    },
                    {
                        "bounds": {
                            "x": 562,
                            "y": 608,
                            "width": 507,
                            "height": 430
                        },
                        "action": {
                            "type": "message",
                            "label": "常見Q&A",
                            "text": "@常見Q&A"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1099,
                            "y": 610,
                            "width": 493,
                            "height": 422
                        },
                        "action": {
                            "type": "message",
                            "label": "分享帳號",
                            "text": "@分享帳號"
                        }
                    },
                ]
            }
            richmenu_id = create(data)
            # 上傳圖片
            upload_image(file, richmenu_id)
            # set alias
            set_alias(richmenu_id, "second_school_info")

def set_english_richmenu():
    
    for file in os.listdir(IMAGE_PATH):
        if file == "多層選單(英文).png":
                # create
                data = {
                    "size": {
                        "width": 1625,
                        "height": 1083
                    },
                    "selected": False,
                    "name": "campus_life",
                    "chatBarText": "More info",
                    "areas": [
                        {
                        "bounds": {
                            "x": 1418,
                            "y": 0,
                            "width": 207,
                            "height": 119
                        },
                        "action": {
                            "type": "postback",
                            "data": "to_chinese",
                        }
                    },
                    {
                        "bounds": {
                            "x": 52,
                            "y": 163,
                            "width": 358,
                            "height": 399
                        },
                        "action": {
                            "type": "uri",
                            "label": "Calender",
                            # 學校網頁改版 the link no longer redirects to calendar
                            # "uri": "https://www.nycu.edu.tw/calendar/"
                            "uri": "https://www.nycu.edu.tw/nycu/en/app/artwebsite/view?module=artwebsite&id=4175&serno=c2d851c9-6641-4cdc-983a-91508dd5eb1d",
                        }
                    },
                    {
                        "bounds": {
                            "x": 431,
                            "y": 177,
                            "width": 348,
                            "height": 380
                        },
                        "action": {
                            "type": "message",
                            "label": "Transportation Info",
                            "text": "¥Transportation Info"
                        }
                    },
                    {
                        "bounds": {
                            "x": 805,
                            "y": 175,
                            "width": 403,
                            "height": 415
                        },
                        "action": {
                            "type": "message",
                            "label": "Dining Info",
                            "text": "¥Dining Info"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1215,
                            "y": 177,
                            "width": 383,
                            "height": 405
                        },
                        "action": {
                            "type": "message",
                            "label": "Emergency Call",
                            "text": "¥Emergency Call"
                        }
                    },
                    {
                        "bounds": {
                            "x": 7,
                            "y": 587,
                            "width": 411,
                            "height": 448
                        },
                        "action": {
                            "type": "message",
                            "label": "Opening Hours",
                            "text": "¥Opening Hours"
                        }
                    },
                    {
                        "bounds": {
                            "x": 825,
                            "y": 585,
                            "width": 356,
                            "height": 470
                        },
                        "action": {
                            "type": "message",
                            "label": "FAQ",
                            "text": "¥FAQ"
                        }
                    },
                    {
                        "bounds": {
                            "x": 1201,
                            "y": 581,
                            "width": 397,
                            "height": 479
                        },
                        "action": {
                            "type": "message",
                            "label": "Campus Safety SOP",
                            "text": "¥Campus Safety SOP"
                        }
                    },
                    {
                        "bounds": {
                            "x": 429,
                            "y": 585,
                            "width": 387,
                            "height": 458
                        },
                        "action": {
                            "type": "message",
                            "label": "Location",
                            "text": "¥Location"
                        }
                    },

                    ]
                }
                richmenu_id = create(data)
                # 上傳圖片
                upload_image(file, richmenu_id)
                # set alias
                set_alias(richmenu_id, "english_campus_life")
                
                with open(ENG_RICHMENU_FILE, 'w') as f:
                    f.write(f'{richmenu_id}\n')

def create(data):
    create_url = "https://api.line.me/v2/bot/richmenu"
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = json.dumps(data, indent=2)
    richmenu_id = requests.post(create_url, data, headers=headers)
    richmenu_id = json.loads(richmenu_id.text)['richMenuId']    
    return richmenu_id


def set_default(richmenu_id):
    set_default_url = f"https://api.line.me/v2/bot/user/all/richmenu/{richmenu_id}"
    res = requests.post(set_default_url, headers={
                        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'})
    print(f"set_default {res}")


def upload_image(file, richmenu_id):
    # 上傳圖片
    api = f'https://api-data.line.me/v2/bot/richmenu/{richmenu_id}/content'
    with open(os.path.join(IMAGE_PATH, file), 'rb') as image:
        headers = {
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
            'Content-Type': 'image/png'
        }
        response = requests.post(api, data=image, headers=headers)
        print(f"upload_image {response}")


def set_alias(richmenu_id, alias):
    api = "https://api.line.me/v2/bot/richmenu/alias"
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
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
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }
    response = requests.get(get_url, headers=headers)
    return json.loads(response.text)


def get_alias():
    get_url = "https://api.line.me/v2/bot/richmenu/alias/list"
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }
    response = requests.get(get_url, headers=headers)
    return json.loads(response.text)


def delete_all():
    rich_menu_dict = get_rich_menus()
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
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
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
            res = requests.post(url, headers=headers)
            print(res.text)
    except Exception as err:
        print(err)
        raise Exception
    
def link_richmenu_to_multiple_users(filename):
    try:
        with open(filename, 'r') as file:
            richmenu_id = file.readline()
            richmenu_id = richmenu_id.strip()
            url = f'https://api.line.me/v2/bot/richmenu/bulk/link'
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}", "Content-Type": "application/json"}
            
            user_ids = pd.read_sql(
                """select t1.user_id, language 
                from 分眾貼標 t1 
                inner join ( 
                    select user_id , max(create_time) most_recent 
                    from 分眾貼標 
                    group by user_id 
                ) t2 on t1.user_id = t2.user_id and t1.create_time = t2.most_recent
                where language='chinese' or language is NULL""", cnxn)

            new_data = pd.read_sql(
                """select distinct user_id from action_record
                where user_id not in (
                    select distinct user_id from 分眾貼標
                )""", cnxn)
            user_ids = pd.concat([new_data, user_ids], ignore_index=True)

            rounds = len(user_ids) // 500 + 1
            for i in range(rounds):
                user_ids_list = user_ids.iloc[i*500:(i+1)*500, :]["user_id"].tolist()
                data = {
                    "richMenuId": richmenu_id,
                    "userIds": user_ids_list
                }
                data = json.dumps(data, indent=2)
                res = requests.post(url, headers=headers, data=data)
                if res.status_code != 202:
                    print(res.text)
                print("Processing Chinese users... " + str(i+1) + "/" + str(rounds), end='\r')
            print("Processing Chinese users... " + str(rounds) + "/" + str(rounds))
            
        with open(ENG_RICHMENU_FILE, 'r') as file:
            richmenu_id = file.readline()
            richmenu_id = richmenu_id.strip()
            url = f'https://api.line.me/v2/bot/richmenu/bulk/link'
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}", "Content-Type": "application/json"}
            
            user_ids = pd.read_sql(
                """select t1.user_id, language 
                from 分眾貼標 t1 
                inner join ( 
                    select user_id , max(create_time) most_recent 
                    from 分眾貼標 
                    group by user_id 
                ) t2 on t1.user_id = t2.user_id and t1.create_time = t2.most_recent
                where language='english'""", cnxn)
            
            rounds = len(user_ids) // 500 + 1
            
            for i in range(rounds):
                user_ids_list = user_ids.iloc[i*500:(i+1)*500, :]["user_id"].tolist()
                data = {
                    "richMenuId": richmenu_id,
                    "userIds": user_ids_list
                }
                data = json.dumps(data, indent=2)
                res = requests.post(url, headers=headers, data=data)
                if res.status_code != 202:
                    print(res.text)
                print("Processing English users... " + str(i+1) + "/" + str(rounds), end='\r')
            print("Processing English users... " + str(rounds) + "/" + str(rounds))
    except:
        raise Exception

if __name__ == "__main__":
    warnings.filterwarnings(
        "ignore", message=".*pandas only supports SQLAlchemy.*")
    parser = argparse.ArgumentParser(description="Richmenu configuration")
    parser.add_argument('-s', '--set', action="store_true", help='Set all richmenus to your line account')
    parser.add_argument('-l', '--link', action="store", choices=['first', 'second'], type=str, help='Link the given semester richmenu to all users. English users will link with english richmenu. Available types: first, second')
    
    
    if parser.parse_args().set or parser.parse_args().link:
        if parser.parse_args().set:
            delete_all()
            set_first_half_semester_rich_menus()
            set_second_half_semester_rich_menus()
            set_english_richmenu()
        if parser.parse_args().link:
            if parser.parse_args().link == "first":
                link_richmenu_to_multiple_users(F_HALF_RICHMENU_FILE)
            elif parser.parse_args().link == "second":
                link_richmenu_to_multiple_users(S_HALF_RICHMENU_FILE)
    else:
        parser.print_help()
        exit(1)
