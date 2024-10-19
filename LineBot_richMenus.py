from config import LINEBOT_ACCESS_TOKEN

import requests
import json
import os
import pandas as pd
from linebot.models import *
from linebot import LineBotApi

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN)

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
                    "uri": "http://140.112.251.50:3000",
                }
            }
        ]
    }
    richmenu_id = create(data)
    # 上傳圖片
    upload_image(file, richmenu_id)
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
