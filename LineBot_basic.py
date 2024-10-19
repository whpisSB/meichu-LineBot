# -*- coding: UTF-8 -*-
#Python module requirement: line-bot-sdk, flask
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent

import time, requests
import os
import threading
# response = requests.get('http://140.112.251.50:5000/health_check')
# print(response.text)
line_bot_api = LineBotApi('4i4FncKooWFGmj3ueylc7KeK7hCTv74mdIb8yXo6kuzgBKvobSS0TEtYr+6AblXnVmyNT4v4DZCu80bhlTtLmdKAqG6m4LZhnURi85YmUR7eyzwFIPNWtXhfM6r/7GygMDbanmYhfjb2jJNSz07fHwdB04t89/1O/w1cDnyilFU=') #LineBot's Channel access token
handler = WebhookHandler('7c4b10c631ec30a9a9a8a88aa186fea8')        #LineBot's Channel secret
user_id_set=set()                                         #LineBot's Friend's user id 
app = Flask(__name__)

def loadUserId():
    try:
        idFile = open('idfile', 'r')
        idList = idFile.readlines()
        idFile.close()
        idList = idList[0].split(';')
        idList.pop()
        return idList
    except Exception as e:
        print(e)
        return None

def saveUserId(userId):
        user_id_set.add(userId)
        idFile = open('idfile', 'a')
        idFile.write(userId+';')
        idFile.close()

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
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    print('\n\nGotMsg:{}\n\n'.format(Msg))
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="歡迎使用黑客組TSMC-2 LineBot\n\n作者: 楊秉宇\n   戚維凌\n   蔡師瑞\n   鄭栩安\n   許訓輔\n\n遇到任何問題請聯絡@an_x0510\n"))
    
    userId = event.source.user_id
    if not userId in user_id_set:
        saveUserId(userId)

@handler.add(PostbackEvent, message=TextMessage)
def handle_message(event):
    Msg = event.message.text
    print('\n\nGotMsg:{}\n\n'.format(Msg))
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="歡迎使用黑客組TSMC-2 LineBot\n\n作者: 楊秉宇\n   戚維凌\n   蔡師瑞\n   鄭栩安\n   許訓輔\n\n遇到任何問題請聯絡@an_x0510\n"))
    
    userId = event.source.user_id
    if not userId in user_id_set:
        saveUserId(userId)

def send_speech2Text_message():
    pass

thread = threading.Thread(target=send_speech2Text_message)
thread.daemon = True
thread.start()

if __name__ == "__main__":
    idList = loadUserId()
    if idList: user_id_set = set(idList)
    print(user_id_set)
    try:
        for userId in user_id_set:
            line_bot_api.push_message(userId, TextSendMessage(text='LineBot is ready for you.'))  # Push API example
    except Exception as e:
        print(e)
    app.run('127.0.0.1', port=32768, threaded=True, use_reloader=False)

    

