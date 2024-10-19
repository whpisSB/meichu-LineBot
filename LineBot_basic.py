# -*- coding: UTF-8 -*-
#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent, ImageSendMessage

from messages import get_reward_message, get_review_message, get_user_reward_message
from api import get_reward_data, exchange_reward, generate_icon, send_review_result, get_user_reward, get_review_history
from config import LINEBOT_ACCESS_TOKEN, LINEBOT_CHANNEL_SECRET
from LineBot_richMenus import link_richmenu_to_user

import time, os, threading, json, re

line_bot_api = LineBotApi(LINEBOT_ACCESS_TOKEN) #LineBot's Channel access token
handler = WebhookHandler(LINEBOT_CHANNEL_SECRET)        #LineBot's Channel secret

# user_id_set=set()                                         #LineBot's Friend's user id 
userId_status = {}                                          #LineBot's Friend's status
reviewer_data = {}
app = Flask(__name__)

def loadUserStatus():
    try:
        with open('data/userStatus.json', 'r') as userStatusFile:
            userStatus = json.load(userStatusFile)
            return userStatus
    except Exception as e:
        print(e)
        return None

def updateUserStatus(userId, status: str):
    with open('data/userStatus.json', 'r+') as userStatusFile:
        userStatus = json.load(userStatusFile)
        userStatus[userId] = status
        userStatusFile.seek(0)
        json.dump(userStatus, userStatusFile)
        userStatusFile.truncate()

        userId_status[userId] = status

def loadUserId():
    try:
        with open('data/userStatus.json', 'r') as userStatusFile:
            userStatus = json.load(userStatusFile)
            return userStatus
    except Exception as e:
        print(e)
        return None

@app.route("/", methods=['GET'])
def hello():
    return "HTTPS Test OK."

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']    # get X-Line-Signature header value
    body = request.get_data(as_text=True)              # get request body as text
    print("Request body: " + body, "Signature: " + signature)
    try:
        handler.handle(body, signature)                # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return "HTTPS Test OK."

# when backend send review request to manager
@app.route("/review", methods=['POST'])
def reviewRequest():
    data = request.get_json()

    messages = get_review_message(data)
    line_id = data["reviewer_id"]
    print(line_id)
    for message in messages:
        line_bot_api.push_message(line_id, message)

    reviewer_data[line_id] = data
    updateUserStatus(line_id, "review")
    
    return jsonify({"message": "ok"}, 200)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    print('\n\nGotMsg:{}\n\n'.format(Msg))
    
    userId = event.source.user_id
    if not userId in userId_status:
        link_richmenu_to_user(userId)
        updateUserStatus(userId, "normal")
    if userId_status[userId] == "reply_prompt":
        updateUserStatus(userId, "normal")
        url = generate_icon(userId, Msg)
        if url:
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=url, preview_image_url=url))
    elif userId_status[userId] == "review":
        if re.match(r'^[1-5]分$', Msg):
            updateUserStatus(userId, "normal")
            data = reviewer_data[userId]
            send_review_result(data, Msg.split('分')[0])
            del reviewer_data[userId]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="感謝您的回覆!"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點選 1~5分"))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="歡迎使用黑客組TSMC-2 LineBot\n\n請點擊選單執行操作\n-----------------------\n作者:\n   楊秉宇\n   戚維凌\n   蔡師睿\n   鄭栩安\n   許訓輔\n\n遇到任何問題請聯絡@an_x0510\n"))

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    if user_id not in userId_status:
        link_richmenu_to_user(user_id)
        updateUserStatus(user_id, "normal")
    data = event.postback.data # postback label
    if data == "myPoints":
        message = get_review_history(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
    elif data == "myPrize":
        rewards = get_user_reward(user_id)
        print(rewards)
        if rewards:
            line_bot_api.reply_message(event.reply_token, get_user_reward_message(rewards))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="尚未獲得獎品"))

    elif data == "showPrizes":
        rewardData = get_reward_data()
        rewardList = get_reward_message(rewardData) if rewardData else None
        if rewardList:
            line_bot_api.reply_message(event.reply_token, rewardList)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有獎品"))
    elif data.split(' ')[0] == "price":
        reward_id = data.split(' ')[1]
        
        if exchange_reward(user_id, reward_id) == "購買成功":
            if reward_id == "3":
                updateUserStatus(user_id, "reply_prompt")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您想要的圖片描述 (限英文)"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="兌換成功\n\n請點選 \"查看獎勵\" 查看"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="兌換失敗"))

if __name__ == "__main__":
    userId_status = loadUserStatus()
    print(userId_status)
    # idList = loadUserId()
    # if idList: user_id_set = set(idList)
    # print(user_id_set)
    # try:
    #     for userId in user_id_set:
    #         if userId_status[userId] == "normal":
    #             line_bot_api.push_message(userId, TextSendMessage(text="歡迎使用黑客組TSMC-2 LineBot\n\n請點擊選單執行操作\n-----------------------\n作者:\n   楊秉宇\n   戚維凌\n   蔡師睿\n   鄭栩安\n   許訓輔\n\n遇到任何問題請聯絡@an_x0510\n"))  # Push API example
    # except Exception as e:
        # print(e)
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

