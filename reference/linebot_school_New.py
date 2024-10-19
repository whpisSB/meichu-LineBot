#!/usr/bin/env python
# coding: utf-8

# sorted imports
from bot_config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from flask import Flask, request, abort, render_template
from flask_wtf import FlaskForm
from imgurpython import ImgurClient
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from NaturalLanguageProcessing.CLU_intent_analyze import *
from richmenu_config import link_richmenu_to_user
from PIL import Image
from richmenu_config import link_richmenu_to_user, F_HALF_RICHMENU_FILE, S_HALF_RICHMENU_FILE, ENG_RICHMENU_FILE
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from sqlalchemy import create_engine
from time import strftime, localtime
from util.Academic_Affair_Office import *
from util.activity import *
from util.admission import *
from util.beacon.fetch_flex_msg import fetch_flex_message
from util.beacon.log import LogBeacon
from util.borrow_rule import *
from util.campus_clinic import *
from util.campus_innovice import *
from util.club import *
from util.course import *
from util.covid_19 import *
from util.credits import *
from util.dormitory import *
from util.english_version import *
from util.freshman import *
from util.graguation import *
from util.introduction import *
from util.labeling import *
from util.library import *
from util.location import *
from util.restaurant import *
from util.SDGs import *
from util.service_learning import *
from util.traffic import *
from wtforms import SubmitField, FileField, TextAreaField, BooleanField
import chromedriver_autoinstaller
import datetime
import json
import numpy as np
import os
import pandas as pd
import pyodbc
import re  # 解決寫入檔案編碼問題
import warnings
from werkzeug.utils import secure_filename


from bot_config import (
    MSSQL_ENGINE,
    MSSQL_DRIVER,
    client_id,
    client_secret,
    access_token,
    refresh_token,
    album_id,
)

engine = create_engine(MSSQL_ENGINE)
cnxn = pyodbc.connect(MSSQL_DRIVER)


# These are intent-based functions


# 過濾SQLAlchemy警告
warnings.filterwarnings(
    "ignore", message=".*pandas only supports SQLAlchemy.*")


def imgur_upload(PATH):
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    config = {
        "album": album_id,
        "name": "test-name!",
        "title": "test-title",
        "description": "test-description",
    }
    print("Uploading image... ")
    imgur_image = client.upload_from_path(PATH, config=config, anon=False)
    print("Done", imgur_image["link"])
    return imgur_image["link"]


# -----------------------------------------------------------------

chromedriver_autoinstaller.install()  # check if there is a new chrome driver


# 校園公告
def announce():
    re_title = []
    re_url = []
    re_span = []
    with open("./data/announce.txt", "r", encoding="utf-8") as f:
        datas = f.read()
        for iter, data in enumerate(datas.split("*")):
            if iter % 2 == 0:
                if len(data) >= 40:
                    re_title.append(data[:39])
                else:
                    re_title.append(data)
            else:
                re_url.append(data)

    return re_title, re_url

QA_title = pd.read_sql("SELECT DISTINCT title FROM QnA WHERE bot_id=1", cnxn)
temp = QA_title["title"].iloc[1]
QA_title.iloc[1] = QA_title.iloc[0]
QA_title.loc[0, "title"] = temp
administrative_unit = pd.read_sql(
    "SELECT DISTINCT[單位],[優先度]  FROM [ChatbotDB].[dbo].[學校各部門連絡方式] WHERE 單位類別='行政單位' AND 學校='交通' ORDER BY 優先度",
    cnxn,
)
teaching_unit = pd.read_sql(
    "SELECT DISTINCT[單位],[優先度]  FROM [ChatbotDB].[dbo].[學校各部門連絡方式] WHERE 單位類別='教學單位' AND 學校='交通' ORDER BY 優先度",
    cnxn,
)
y_administrative_unit = pd.read_sql(
    "SELECT DISTINCT[單位],[優先度]  FROM [ChatbotDB].[dbo].[學校各部門連絡方式] WHERE 單位類別='行政單位' AND 學校='陽明' ORDER BY 優先度",
    cnxn,
)
y_teaching_unit = pd.read_sql(
    "SELECT DISTINCT[單位],[優先度]  FROM [ChatbotDB].[dbo].[學校各部門連絡方式] WHERE 單位類別='教學單位' AND 學校='陽明' ORDER BY 優先度",
    cnxn,
)
all_unit = pd.concat([administrative_unit, teaching_unit])
y_all_unit = pd.concat([y_administrative_unit, y_teaching_unit])
contact_text = np.array(pd.read_csv(
    "contact_method2.csv", encoding="utf-8"))  # 各處室分機


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
user_question = ""
user_id_label_dict = {}  # data: (user_id: label_info), type: (str:str) 貼標用


class FileUploadForm(FlaskForm):
    file = FileField('Upload File')
    submit = SubmitField('Submit')
    description = TextAreaField('Description')
    # identity_choices = [("match_all", "不指定"), ("在校生", "在校生"), ("校友", "校友"), ("教職員", "教職員"), ("一般民眾", "一般民眾")]
    # degree_choices = [("match_all", "不指定"), ("學士", "學士"), ("碩士", "碩士"), ("博士", "博士")]
    # degree_year = [("match_all", "不指定"), ("大一", "大一"), ("大二", "大二"), ("大三", "大三"), ("大四", "大四"), ("大五(以上)", "大五(以上)"), ("碩一", "碩一"), ("碩二", "碩二"), ("碩三(以上)", "碩三(以上)"), ("博一", "博一"), ("博二", "博二"), ("博三", "博三"), ("博四(以上)", "博四(以上)")]
    # group_choices = [("match_all", "不指定"), ("人社法商管", "人社法商管"), ("科學理工", "科學理工"), ("生物醫藥護", "生物醫藥護")]
    # intent_choices = [("match_all", "不指定"), ("覓食", "覓食"), ("休憩", "休憩"), ("演講，研討會", "演講，研討會"), ("參加營隊", "參加營隊"), ("場地使用", "場地使用"), ("其他", "其他")]
    # department_choices = [("match_all", "不指定"), ("學院系所", "學院系所"), ("行政單位", "行政單位")]

    identity_1 = BooleanField("在校生")
    identity_2 = BooleanField("校友")
    identity_3 = BooleanField("教職員")
    identity_4 = BooleanField("一般民眾")

    degree_1 = BooleanField("學士")
    degree_2 = BooleanField("碩士")
    degree_3 = BooleanField("博士")

    year_1 = BooleanField("大一")
    year_2 = BooleanField("大二")
    year_3 = BooleanField("大三")
    year_4 = BooleanField("大四")
    year_5 = BooleanField("大五(以上)")
    year_6 = BooleanField("碩一")
    year_7 = BooleanField("碩二")
    year_8 = BooleanField("碩三(以上)")
    year_9 = BooleanField("博一")
    year_10 = BooleanField("博二")
    year_11 = BooleanField("博三")
    year_12 = BooleanField("博四(以上)")

    group_1 = BooleanField("人社法商管")
    group_2 = BooleanField("科學理工")
    group_3 = BooleanField("生物醫藥護")

    intent_1 = BooleanField("覓食")
    intent_2 = BooleanField("休憩")
    intent_3 = BooleanField("演講，研討會")
    intent_4 = BooleanField("參加營隊")
    intent_5 = BooleanField("場地使用")
    intent_6 = BooleanField("其他")

    department_1 = BooleanField("學院系所")
    department_2 = BooleanField("行政單位")




@app.route("/broadcast", methods=['GET', 'POST'])
def broadcast():
    form = FileUploadForm()
    if form.is_submitted() and form.validate():
        file = form.file.data
        desc = form.description.data
        mimetype = file.mimetype.split('/')
        fname = secure_filename(file.filename)

        choices = [[form.identity_1, form.identity_2, form.identity_3, form.identity_4],
                    [form.degree_1, form.degree_2, form.degree_3],
                    [form.year_1, form.year_2, form.year_3, form.year_4, form.year_5, form.year_6,
                    form.year_7, form.year_8, form.year_9, form.year_10, form.year_11, form.year_12],
                    [form.group_1, form.group_2, form.group_3],
                    [form.intent_1, form.intent_2, form.intent_3, form.intent_4, form.intent_5, form.intent_6],
                    [form.department_1, form.department_2]]

        choices = [[i.label.text for i in row if i.data] for row in choices]
        print("Selected filters:\n", choices)

        query = """
                with latest_entries as (
                    select * from (
                        select *, ROW_NUMBER() over (partition by [user_id] order by [create_time] desc) as rn
                        from [dbo].[分眾貼標]
                    ) as newest where rn = 1)
                select user_id from latest_entries where"""

        for clause in choices:
            if len(clause) != 0:
                query += ' (' if query.endswith('where') else ' and ('

                for sub_clause in clause:
                    query += "label like '%" + sub_clause + "%' or "

                query = query[:-4] + ')'

        if query.endswith('where'):
            query = "select distinct user_id from [dbo].[action_record]"

        print(query)

        try:
            message = []
            userIds = pd.read_sql(query, cnxn)['user_id']
            #userIds = ['Uf2038f6833bbc65d2f79f0a6b651fa06']

            if desc is not None:
                message.append(TextSendMessage(desc))

            if mimetype[1] == 'json':
                print("Json object")
                json_data = json.load(file)
                
                message.append(FlexSendMessage(alt_text='推播訊息', contents=json_data))
            elif mimetype[0] == 'image':
                print("Image object")

                if not os.path.isdir('tmp'):
                    print("No \"tmp\" directory found. Creating...")
                    os.mkdir('tmp')

                path = os.path.join(os.getcwd(), 'tmp', fname)
                file.save(path)
                link = imgur_upload(path)
                print(link)
                message.append(ImageSendMessage(original_content_url=link, preview_image_url=link))

            print(f"broadcasting to {len(userIds)} users")
            # for userId in userIds:
            #     # print(f"sent message to {userId}")
            #     try:
            #         line_bot_api.push_message(userId, message)
            #     except:
            #         print("Failed to push message to", userId)
            line_bot_api.multicast(userIds.to_list(), message)

            print(f"broadcast complete")
        except Exception as e:
            print(e)

    return render_template('index.html', form=form)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as err:
        print("可能是你Line access token或channel secret設錯了喔")
        abort(400)
    return "", 200


@handler.add(BeaconEvent)
def handle_beacon(event):
    beacon_type = event.beacon.type
    beacon_hwid = event.beacon.hwid
    timestamp = event.timestamp
    user_id = event.source.user_id

    # {hardware id} : {location name}
    beacons = {
        "0000052d7f": "交清小徑",
        "0000052d76": "研三舍",
        "0000052d72": "浩然圖書館",
        "0000052d78": "女二舍",
        "0000052d7a": "交大藝文中心",
        "0000052d7b": "活動中心",
        "0000052d7e": "二餐",
        "0000052d74": "一餐",
        "0000052d79": "大禮堂",
        "0000052d71": "人社三館",
        "0000052d70": "二餐（備用）",
        # "0000052d67": "環校機車道", # used for testing
    }

    def convert_unix_timestamp(timestamp_ms: int) -> str:
        timestamp_sec = int(timestamp_ms / 1000)
        dt = datetime.datetime.utcfromtimestamp(timestamp_sec)
        dt_adjusted = dt + datetime.timedelta(hours=8)  # UTC+8
        return dt_adjusted.strftime("%Y-%m-%d %H:%M:%S")
    
    if beacon_type == "enter" or beacon_type == "stay":
        # try:
        if beacons.get(str(beacon_hwid)) is not None:
            alt_text, flex_msg = fetch_flex_message(beacons.get(str(beacon_hwid)))
            if alt_text is None:
                alt_text = "beacon message"
            message = FlexSendMessage(alt_text, flex_msg)
            line_bot_api.reply_message(event.reply_token, message)

            log_beacon = LogBeacon(
                user_id=user_id,
                time=convert_unix_timestamp(timestamp),
                beacon_action=beacon_type,
                beacon_hwid=beacon_hwid,
                beacon_location=beacons.get(str(beacon_hwid))
            )
            #log beacon into database
            log_beacon.register_changes()
        else:
            print("beacon not found: beacon_hwid = " + str(beacon_hwid))
        # except Exception as e:
        #     print(e)
    # elif beacon_type == "banner":
    #     ...  # all it does is literally just adding a friend. 🥺
    #     # message = "you have clicked on a beacon banner\nbeacon hwid: " + \
    #     #     str(beacon_hwid) + "\nAre you at " + \
    #     #     str(beacons.get(str(beacon_hwid))) + "?"
    #     # message = TextSendMessage(text=message)
    #     # line_bot_api.reply_message(event.reply_token, message)


@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    
# 112上學期開學分眾活動=====================================================================================================
    
    user_id_label_dict[user_id] = None
    img_message = labeling_main()
    line_bot_api.reply_message(event.reply_token, img_message)

# ====================================================================================================================
    # link_richmenu_to_user(user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id_label_dict
    detail_Flag = False
    detail_request = ""
    user_id = event.source.user_id
    origin_mtext = event.message.text
    action_kind = "其他選項"
    research_type = -1
    if ("@✦★#¥".find(origin_mtext[0])) == -1:
        origin_kind = "文字輸入"
        action_kind = "文字輸入(非回饋時)"
        research_type = 1
    else:
        origin_kind = "按鈕選擇"
        action_kind = "其他選項"
        research_type = 0

    mtext = ask_detail(origin_mtext, user_id)
    user_question = mtext
    mtext, detail_Flag, detail_request = check_if_button_click(mtext)
    now_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

    suggest_flag = False
    message_flag = False

    # 如果是課號的話會直接回傳課號所在上課地點
    if mtext[0] == '¥':
        try:
            if user_id in user_id_label_dict:
                del user_id_label_dict[user_id]
            action_kind, message = handle_english_message_event(mtext, user_question, user_id, cnxn, now_time)
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            print(e)
            message = TextSendMessage(text="An unexpected error occured.")
            line_bot_api.reply_message(event.reply_token, message)
    elif len(mtext) == 6 and mtext.isdigit():
        try:
            message = find_location_by_class_id(mtext)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "結束":
        message = TextSendMessage(text="沒有對話可以結束")
        line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@緊急聯絡電話":
        action_kind = "緊急聯絡電話"
        message = emergency_contact()
        line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@社團活動/沒指定" or mtext == "@社團活動":
        mtext = "@社團活動/沒指定"
        try:
            action_kind = "社團活動"
            message = club_activity(mtext, user_id)
            print("y")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@查詢教室、處室位置":
        try:
            action_kind = "教務資訊"
            message = get_location_info(mtext, user_id)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教務資訊":
        try:
            action_kind = "教務資訊"
            message = academic_affairs()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@課務組":
        try:
            action_kind = "教務資訊"
            message = academic_affairs_course()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@註冊組":
        try:
            action_kind = "教務資訊"
            message = academic_affairs_registration()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教學發展中心":
        try:
            action_kind = "教務資訊"
            message = academic_affairs_teaching_center()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@課程":
        try:
            action_kind = "教務資訊"
            message = course()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教室":
        try:
            action_kind = "教務資訊"
            message = classroom_ques()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學分費":
        try:
            action_kind = "教務資訊"
            message = course_credit()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@聯絡資訊":
        try:
            action_kind = "教務資訊"
            message = contact()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學期選課":
        try:
            action_kind = "教務資訊"
            message = course_QA()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@課程資訊":
        try:
            action_kind = "教務資訊"
            message = course_info()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@課程停修":
        try:
            action_kind = "教務資訊"
            message = course_withdraw()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教室情形":
        try:
            action_kind = "教務資訊"
            message = classroom_condition()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教室借用":
        try:
            action_kind = "教務資訊"
            message = classroom_rent()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@是否繳交學分費":
        try:
            action_kind = "教務資訊"
            message = course_credit_need()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學分費繳交方式":
        try:
            action_kind = "教務資訊"
            message = course_credit_how()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學分費繳交期限":
        try:
            action_kind = "教務資訊"
            message = course_credit_when()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@跨域學程":
        try:
            action_kind = "教務資訊"
            message = cross_disciplinary()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@如何申請跨域":
        try:
            action_kind = "教務資訊"
            message = cross_join()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@跨域申請限制":
        try:
            action_kind = "教務資訊"
            message = cross_restrict()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@輔導機制":
        try:
            action_kind = "教務資訊"
            message = cross_help()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@跨域各類申請表":
        try:
            action_kind = "教務資訊"
            message = cross_application_form()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學倫課程":
        try:
            action_kind = "教務資訊"
            message = academic_ethics()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學倫修課對象":
        try:
            action_kind = "教務資訊"
            message = academic_ethics_who()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學倫上課方式":
        try:
            action_kind = "教務資訊"
            message = academic_ethics_how()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學倫應於何時修畢":
        try:
            action_kind = "教務資訊"
            message = academic_ethics_when()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學倫課程抵免":
        try:
            action_kind = "教務資訊"
            message = academic_ethics_credit()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學習工坊活動":
        try:
            action_kind = "教務資訊"
            message = workshop()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@一對一輔導":
        try:
            action_kind = "教務資訊"
            message = on_person()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@成績單相關":
        try:
            action_kind = "教務資訊"
            message = score_sheet()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@文件申請":
        try:
            action_kind = "教務資訊"
            message = score_sheet_apply()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@成績單辦理":
        try:
            action_kind = "教務資訊"
            message = score_sheet_handle()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@在校成績":
        try:
            action_kind = "教務資訊"
            message = score_sheet_at_school()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@文件申請成績單":
        try:
            action_kind = "教務資訊"
            message = apply_type_score()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@文件申請證明文件":
        try:
            action_kind = "教務資訊"
            message = apply_type_proof()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@自動繳費機辦理":
        try:
            action_kind = "教務資訊"
            message = handle_auto()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@線上辦理":
        try:
            action_kind = "教務資訊"
            message = handle_online()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@特例辦理":
        try:
            action_kind = "教務資訊"
            message = handle_special()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@有排名在校成績":
        try:
            action_kind = "教務資訊"
            message = at_school_rank()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@GPA轉成績":
        try:
            action_kind = "教務資訊"
            message = GPA_to_real()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試":
        try:
            action_kind = "教務資訊"
            message = degree_test()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試成績繳交":
        try:
            action_kind = "教務資訊"
            message = degree_score()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試相關表件":
        try:
            action_kind = "教務資訊"
            message = degree_need()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試舉行方式":
        try:
            action_kind = "教務資訊"
            message = degree_holding_way()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試申請期限":
        try:
            action_kind = "教務資訊"
            message = degree_apply_cutoff()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學位考試申請程序":
        try:
            action_kind = "教務資訊"
            message = degree_apply_procedure()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學籍相關":
        try:
            action_kind = "教務資訊"
            message = school_register()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新生註冊":
        try:
            action_kind = "教務資訊"
            message = freshman()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新生資料":
        try:
            action_kind = "教務資訊"
            message = freshman_info()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@開學":
        try:
            action_kind = "教務資訊"
            message = school_open()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新生繳費":
        try:
            action_kind = "教務資訊"
            message = freshman_register_fee()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@新生活動", "@新生其他"]:
        try:
            action_kind = "教務資訊"
            message = freshman_other()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@畢業離校":
        try:
            action_kind = "教務資訊"
            message = graduate()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新生如何選課":
        try:
            action_kind = "教務資訊"
            message = course_QA1()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@無法登入選課系統":
        try:
            action_kind = "教務資訊"
            message = course_QA2()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@選不到課程應如何處理":
        try:
            action_kind = "教務資訊"
            message = course_QA3()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@必修課程是否需要加選":
        try:
            action_kind = "教務資訊"
            message = course_QA4()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@如何辦理校際選課":
        try:
            action_kind = "教務資訊"
            message = course_QA5()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@課程加選失敗":
        try:
            action_kind = "教務資訊"
            message = course_QA6()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@畢業生須知":
        try:
            action_kind = "教務資訊"
            message = graduate_info()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@畢業資格":
        try:
            action_kind = "教務資訊"
            message = graduate_qualification()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@辦理時間與地點":
        try:
            action_kind = "教務資訊"
            message = graduate_handle()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@領取證書":
        try:
            action_kind = "教務資訊"
            message = graduate_recieve()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學雜費":
        try:
            action_kind = "教務資訊"
            message = tuition_fee()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@繳交學雜費":
        try:
            action_kind = "教務資訊"
            message = tuition_fee_how()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學雜費金額":
        try:
            action_kind = "教務資訊"
            message = tuition_fee_how_much()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學雜費期限":
        try:
            action_kind = "教務資訊"
            message = tuition_fee_when()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學雜費補交":
        try:
            action_kind = "教務資訊"
            message = tuition_fee_late()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@雙主修/輔系及學分抵免":
        try:
            action_kind = "教務資訊"
            message = double_major_and_others()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@雙主修/輔系":
        try:
            action_kind = "教務資訊"
            message = double_major()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@雙主修申請":
        try:
            action_kind = "教務資訊"
            message = double_major_apply()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@雙主修時間":
        try:
            action_kind = "教務資訊"
            message = double_major_when()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學分抵修與免修":
        try:
            action_kind = "教務資訊"
            message = credit_replace()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@抵免定義":
        try:
            action_kind = "教務資訊"
            message = credit_replace_def()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學分抵免申請":
        try:
            action_kind = "教務資訊"
            message = credit_replace_apply()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@資料異動與休退學":
        try:
            action_kind = "教務資訊"
            message = info_modification()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@個人基本資料異動":
        try:
            action_kind = "教務資訊"
            message = personal_info_modify()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@個人照片異動":
        try:
            action_kind = "教務資訊"
            message = photo_modify()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休退學申請規則":
        try:
            action_kind = "教務資訊"
            message = quit_school_rule()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休退學申請":
        try:
            action_kind = "教務資訊"
            message = quit_school_apply()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休學辦理時間":
        try:
            action_kind = "教務資訊"
            message = quit_school_when()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休學期限":
        try:
            action_kind = "教務資訊"
            message = quit_school_length()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休學特例":
        try:
            action_kind = "教務資訊"
            message = quit_school_special()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@休退學學雜費":
        try:
            action_kind = "教務資訊"
            message = quit_school_tuition_fee()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@分享帳號":
        try:
            action_kind = "分享帳號"
            message = share()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@YouBike資訊":
        try:
            action_kind = "交通資訊"
            message = [
                TextSendMessage(text="小幫手正在幫您抓取資料!\n請稍後..."),
                ImageSendMessage(
                    original_content_url="https://imgur.com/QM7t9sj.jpg",
                    preview_image_url="https://imgur.com/QM7t9sj.jpg",
                ),
                ImageSendMessage(
                    original_content_url="https://imgur.com/sUqliPy.jpg",
                    preview_image_url="https://imgur.com/sUqliPy.jpg",
                ),
                UBIKE(mtext[1:]),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@位置資訊":
        try:
            action_kind = "位置資訊"
            message = button_place_information()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@校區地圖":
        try:
            action_kind = "位置資訊"
            message = [
                TextSendMessage(text="請點選地圖以查看Google Map! "),
                button_school_map(),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@停車地圖":
        try:
            action_kind = "位置資訊"
            message = [
                TextSendMessage(text="請點選地圖以查看Google Map! "),
                button_school_parking_map(),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@系所規定":
        try:
            action_kind = "教務資訊"
            message = department_of_regulation()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@常見Q&A":
        try:
            action_kind = "常見QA"
            message = button_QA_NYCU()
            line_bot_api.reply_message(event.reply_token, message)
            # line_bot_api.reply_message(event.reply_token, QA_first_layer())
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@常見Q&A(陽明交大)":
        try:
            action_kind = "常見QA"
            message = button_QA_NYCU()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)

    elif mtext == "@交通資訊":
        try:
            action_kind = "交通資訊"
            # message = button_travel(mtext[1:])
            message = traffic_image_map(mtext[1:])
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)

    elif mtext == "@近期活動":
        try:
            action_kind = "近期活動"
            message = button_recent_activities()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)

    elif mtext == "@藝文展演":
        try:
            action_kind = "近期活動"
            message = art_culture_nctu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)

    elif mtext == "@視覺藝術":
        try:
            action_kind = "近期活動"
            message = visual_art()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@表演藝術":
        try:
            action_kind = "近期活動"
            message = performance_art()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@演講/研討會":
        try:
            action_kind = "近期活動"
            message = speech_seminar_nctu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@體育活動":
        try:
            action_kind = "近期活動"
            message = sport_game_nctu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@市府藝文活動":
        try:
            action_kind = "近期活動"
            message = outdoor_base()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新竹市藝文活動":
        try:
            action_kind = "近期活動"
            message = outdoor_nctu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@台北市藝文活動":
        try:
            action_kind = "近期活動"
            message = outdoor_nycu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@各處室位置分機":
        try:
            action_kind = "位置資訊"
            message = contact_first_layer()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@各處室位置分機(交通)":
        try:
            action_kind = "位置資訊"
            message = jiau()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@各處室位置分機(陽明)":
        try:
            action_kind = "位置資訊"
            message = yawn()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@行政單位(交通)":
        try:
            action_kind = "位置資訊"
            message = unit_button("行政單位")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教學單位(交通)":
        try:
            action_kind = "位置資訊"
            message = unit_button("教學單位")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@行政單位(陽明)":
        try:
            action_kind = "位置資訊"
            message = y_unit_button("行政單位(陽)")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教學單位(陽明)":
        try:
            action_kind = "位置資訊"
            message = y_unit_button("教學單位(陽)")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@場館營業時間":
        try:
            action_kind = "場館營業時間"
            message = opening_hours()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明校區場館營業時間":
        try:
            action_kind = "場館營業時間"
            message = opening_hours_ym()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@球館及球場營業時間(陽明校區)":
        try:
            action_kind = "場館營業時間"
            message = TextSendMessage(
                text="[綜合球場]\n每日 08:00~22:30\n連續假期、國定假日不開放\n"
                + "-" * 20
                + "\n"
                + "[山下球場（籃球、排球及網球）]\n每日 06:00~22:00\n"
                + "-" * 20
                + "\n"
                + "[山頂球場（籃球、排球及網球）]\n週一~週五 06:00~22:00\n六日晚上不開燈\n"
                + "-" * 20
                + "\n"
                + "[桌球教室]\n每日 08:00~22:30\n連續假期、國定假日不開放"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@游泳健身館營業時間":
        try:
            action_kind = "場館營業時間"
            message = TextSendMessage(
                text="週一~週五 07:00~12:00, 13:00~22:00\n例假日、國定假日 09:00~12:00, 13:00~22:00"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@其他運動場館營業時間":
        try:
            action_kind = "場館營業時間"
            message = TextSendMessage(
                text="[重訓室、心肺功能室]\n每日 08:00~22:30\n連續假期、國定假日不開放\n"
                + "-" * 20
                + "\n"
                + "[韻律教室]\n週一~週五 08:00~22:30\n"
                + "-" * 20
                + "\n"
                + "[山頂運動場]\n週一~週五 06:00~22:00\n六日晚上不開燈"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復校區場館營業時間":
        try:
            action_kind = "場館營業時間"
            message = opening_hours_ct()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@圖書館相關規定":
        try:
            action_kind = "場館營業時間"
            message = library(mtext)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@圖書館營業時間":
        try:
            action_kind = "場館營業時間"
            message = library_hours(mtext)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@圖書館借還書":
        try:
            action_kind = "場館營業時間"
            message = library_detail_behavior(mtext)
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@體育館營業時間":
        try:
            action_kind = "場館營業時間"
            message = stadium_hours()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@游泳館營業時間":
        try:
            action_kind = "場館營業時間"
            message = swimming_hours()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@球館及球場營業時間(光復校區)":
        try:
            action_kind = "場館營業時間"
            message = court_hours()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@SDGs":
        try:
            action_kind = "SDGs"
            message = button_SDGs()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@認識SDGs":
        try:
            action_kind = "SDGs"
            message = [
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/QC88gsC.png",
                    preview_image_url="https://i.imgur.com/QC88gsC.png",
                ),
                TextSendMessage(text=What_is_SDGS()[0]),
                TextSendMessage(text=What_is_SDGS()[1]),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學院永續成果":
        try:
            action_kind = "SDGs"
            message = [
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/dpmqYgs.png",
                    preview_image_url="https://i.imgur.com/dpmqYgs.png",
                ),
                TextSendMessage(text=SDGS_In_NYCU()[0]),
                TextSendMessage(text=SDGS_In_NYCU()[1]),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@NYCU永續成果":
        try:
            action_kind = "SDGs"
            message = SDGs_results()
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@SDGs小遊戲":
        try:
            action_kind = "SDGs"
            message = SDGslottery()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@再抽一次":
        try:
            action_kind = "SDGs"
            message = SDGslottery()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@校區間校車":
        try:
            action_kind = "交通資訊"
            message = school_bus_base(mtext[1:])
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@小紅巴":
        try:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage("小幫手正在幫您抓取資料!\n請稍後...")
            )
            action_kind = "交通資訊"
            message = redline_bus_info(mtext[1:])
            line_bot_api.push_message(user_id, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@豪泰客運":
        try:
            action_kind = "交通資訊"
            message = howtai_bus_base(mtext[1:])
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@豪泰客運[2011]路線圖":
        try:
            action_kind = "交通資訊"
            message = ImageSendMessage(
                original_content_url="https://i.imgur.com/HWBix48.png",
                preview_image_url="https://i.imgur.com/HWBix48.png",
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@豪泰客運中華大學[2011B]":
        try:
            action_kind = "交通資訊"
            message = [
                TextSendMessage(text=howtai_info("2011B")[0]),
                TextSendMessage(text=howtai_info("2011B")[1]),
                TextSendMessage(text=howtai_info("2011B")[2]),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@豪泰客運新竹線[2011]":
        try:
            action_kind = "交通資訊"
            message = [
                TextSendMessage(text=howtai_info("2011")[0]),
                TextSendMessage(text=howtai_info("2011")[1]),
                TextSendMessage(text=howtai_info("2011")[2]),
            ]
            line_bot_api.reply_message(event.reply_token, message)
            # howtai
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明校區內校車":
        try:
            action_kind = "交通資訊"
            message = school_bus_base_nymu(mtext[1:])
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復 <=> 火車站":
        try:
            action_kind = "交通資訊"
            message = [
                school_bus3(),
                TextSendMessage(
                    text="詳情請查看官方網站 : \n"
                    + "光復<=>火車站(往返) \n "
                    + "<https://tinyurl.com/y6ttm3uy>"
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復 <=> 博愛":
        try:
            action_kind = "交通資訊"
            message = [
                school_bus1(),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/Qupzna4.png",
                    preview_image_url="https://i.imgur.com/Qupzna4.png",
                ),
                TextSendMessage(
                    text="詳情請查看官方網站 : \n"
                    + "光復<=>博愛/客院(往返) \n "
                    + "<https://www.eup.tw/shuttle/transport_car.html?68>"
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復 <=> 客院(高鐵)":
        try:
            action_kind = "交通資訊"
            message = [
                school_bus2(),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/6jdKNjZ.png",
                    preview_image_url="https://i.imgur.com/6jdKNjZ.png",
                ),
                TextSendMessage(
                    text="詳情請查看官方網站 : \n"
                    + "光復<=>博愛/客院(往返) \n "
                    + "<https://www.eup.tw/shuttle/transport_car.html?68>"
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明 <=> 光復":
        try:
            action_kind = "交通資訊"
            message = school_bus_nycu()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明綠線校車":
        try:
            action_kind = "交通資訊"
            message = school_bus_nymu_green()
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明紅線校車":
        try:
            action_kind = "交通資訊"
            message = school_bus_nymu_red()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@559路公車":
        try:
            action_kind = "交通資訊"
            # line_bot_api.reply_message(
            #     event.reply_token, TextSendMessage("小幫手正在幫您抓取資料!\n請稍後...")
            # )
            message = bus_559_message()
            print(len(message))
            line_bot_api.push_message(user_id, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@一般徵才":
        try:
            action_kind = "工讀資訊"
            message = job_new()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            action_kind = "工讀資訊"
            message = job()
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@家教資訊":
        try:
            action_kind = "工讀資訊"
            message = tutor()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@帳號開通":
        try:
            action_kind = "校園資訊"
            message = account_creation()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@工讀資訊":
        try:
            action_kind = "工讀資訊"
            message = all_jobs()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@校園公告":
        try:
            action_kind = "校園資訊"
            message = announcement()
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@游泳館、體育館即時人數":
        try:
            action_kind = "校園資訊"
            message = gym_base()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@游泳館健身房人數":
        try:
            action_kind = "校園資訊"
            message = get_gym_crowd(user_question)[0]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@游泳館游泳池人數":
        try:
            action_kind = "校園資訊"
            message = get_pool_crowd(user_question)[0]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@體育館重訓室人數":
        try:
            action_kind = "校園資訊"
            message = get_train_crowd(user_question)[0]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復校區":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="光復校區",
                    address="光復校區",
                    latitude=24.788058942789625,
                    longitude=120.99751744782343,
                ),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/dyEyhU0.png",
                    preview_image_url="https://i.imgur.com/dyEyhU0.png",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@光復校區停車地圖":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="光復校區位置",
                    address="光復校區位置",
                    latitude=24.788058942789625,
                    longitude=120.99751744782343,
                ),
                ImageSendMessage(
                    original_content_url="https://imgur.com/0DypDzl.jpg",
                    preview_image_url="https://imgur.com/0DypDzl.jpg",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@博愛校區":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="博愛校區",
                    address="博愛校區",
                    latitude=24.798162005867532,
                    longitude=120.98163415727078,
                ),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/hujyiJG.jpg",
                    preview_image_url="https://i.imgur.com/hujyiJG.jpg",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明校區":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="陽明校區",
                    address="陽明校區",
                    latitude=25.120115232659725,
                    longitude=121.51434367033437,
                ),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/QDGaBZi.jpg",
                    preview_image_url="https://i.imgur.com/QDGaBZi.jpg",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@陽明校區停車地圖":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="陽明校區位置",
                    address="陽明校區位置",
                    latitude=25.120115232659725,
                    longitude=121.51434367033437,
                ),
                ImageSendMessage(
                    original_content_url="https://imgur.com/W6rJJR2.jpg",
                    preview_image_url="https://imgur.com/W6rJJR2.jpg",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@六家校區":
        try:
            action_kind = "位置資訊"
            message = [
                LocationSendMessage(
                    title="六家校區",
                    address="六家校區",
                    latitude=24.812388621761784,
                    longitude=121.02327731124883,
                ),
                ImageSendMessage(
                    original_content_url="https://i.imgur.com/zdbNQvp.jpg",
                    preview_image_url="https://i.imgur.com/zdbNQvp.jpg",
                ),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@台北校區":
        try:
            action_kind = "位置資訊"
            message = LocationSendMessage(
                title="台北校區",
                address="台北校區",
                latitude=25.047563120475218,
                longitude=121.51188885542783,
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@蘭陽院區":
        try:
            action_kind = "位置資訊"
            message = LocationSendMessage(
                title="蘭陽院區",
                address="蘭陽院區",
                latitude=24.752616623415665,
                longitude=121.75833433862674,
            )
            line_bot_api.reply_message(event.reply_token, message)

        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@新民院區":
        try:
            action_kind = "位置資訊"
            message = LocationSendMessage(
                title="新民院區",
                address="新民院區",
                latitude=24.761381264728406,
                longitude=121.7545083227465,
            )
            line_bot_api.reply_message(event.reply_token, message)

        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@台南校區":
        try:
            action_kind = "位置資訊"
            message = LocationSendMessage(
                title="台南校區",
                address="台南校區",
                latitude=22.924997850767003,
                longitude=120.29494972656654,
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@問題回饋":
        try:
            action_kind = "問題回饋"
            message = TextSendMessage(text="請輸入您遇到的問題或回饋 :")
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    # temporary fix for scholarship garbled luis link shit
    # TODO
    elif mtext == "@有哪些獎學金+申請流程":
        try:
            message = TemplateSendMessage(
                alt_text='scholarship',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            title="獎學金申請流程",
                            text="請參考生輔組獎學金申請流程",
                            actions=[
                                URITemplateAction(
                                    label='連結',
                                    uri="https://sasystem.nycu.edu.tw/scholarship/doc/step1.pdf"
                                )
                            ]
                        ),
                        CarouselColumn(
                            title="有哪些校外獎學金呢",
                            text="獎學金系統內有各式獎學金及內容",
                            actions=[
                                URITemplateAction(
                                    label='連結',
                                    uri="https://sasystem.nycu.edu.tw/scholarship/index2.php"
                                ),
                            ]
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@獎學金申請":
        try:
            action_kind = "獎學金"
            message = scholarship()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@國際交換":
        try:
            action_kind = "國際交換"
            message = abroad()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@交換申請公告":
        try:
            action_kind = "國際交換"
            message = exchange_anouncement()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@可交換列表":
        try:
            action_kind = "國際交換"
            message = TextSendMessage(
                text="列表連結:\nhttps://docs.google.com/spreadsheets/d/1qMgQZnLVICu7b1djo-FMyBDZKvQoMai4vw-hGPq9fw0/edit#gid=1021089665"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@申請說明會簡報":
        try:
            action_kind = "國際交換"
            message = TextSendMessage(
                text="簡報連結:\nhttps://www.canva.com/design/DAFjoQUCmVA/QXXfxBq_BjrIpebqpYhdxQ/view?utm_content=DAFjoQUCmVA&utm_campaign=designshare&utm_medium=link&utm_source=homepage_design_menu"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@交換獎學金":
        try:
            action_kind = "國際交換"
            message = exchange_scholarship()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@回答問題領小禮物":
        try:
            action_kind = "貼標"
            message = labeling_cover()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@中文":
        try:
            action_kind = "貼標"
            message = labeling_character()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@在校生":
        try:
            action_kind = "貼標"
            message = labeling_academic()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif re.fullmatch("[1345][0-9][0-9]{7}", mtext):
        try:
            action_kind = "貼標"
            label = parse_id(mtext)
            user_id_label_dict[user_id] = label
            message = labeling_know_from()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif re.fullmatch("[0-9]{7}", mtext):
        try:
            action_kind = "貼標"
            label = parse_id(mtext)
            user_id_label_dict[user_id] = label
            message = labeling_know_from()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@學士":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_bachelor()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@碩士":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_master()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@博士":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_phd()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@大一", "@大二", "@大三", "@大四", "@大五(以上)"]:
        try:
            action_kind = "貼標"
            # 判斷有沒有重複按到
            info = user_id_label_dict[user_id]
            if info == ["學士"]:
                info.append(mtext[1:])
            elif info[0] == "學士":
                info = [info[0], mtext[1:]]
            user_id_label_dict[user_id] = info
            message = labeling_academic_group_undergraduate()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@碩一", "@碩二", "@碩三(含)以上"]:
        try:
            action_kind = "貼標"
            # 判斷有沒有重複按到
            info = user_id_label_dict[user_id]
            if info == ["碩士"]:
                info.append(mtext[1:])
            elif info[0] == "碩士":
                info = [info[0], mtext[1:]]
            user_id_label_dict[user_id] = info
            message = labeling_academic_group_undergraduate()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@博一", "@博二", "@博三", "@博四(含)以上"]:
        try:
            action_kind = "貼標"
            # 判斷有沒有重複按到
            info = user_id_label_dict[user_id]
            if info == ["博士"]:
                info.append(mtext[1:])
            elif info[0] == "博士":
                info = [info[0], mtext[1:]]
            user_id_label_dict[user_id] = info
            message = labeling_academic_group_undergraduate()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@人社法商管", "@生物醫藥護", "@科學理工"]:
        try:
            action_kind = "貼標"
            # 判斷有沒有重複按到
            info = user_id_label_dict[user_id]
            is_bachelor = info[0] == "學士" and info[1] in [
                "大一", "大二", "大三", "大四", "大五(以上)"]
            is_master = info[0] == "碩士" and info[1] in ["碩一", "碩二", "碩三(含)以上"]
            is_phd = info[0] == "博士" and info[1] in [
                "博一", "博二", "博三", "博四(含)以上"]
            is_alumi = info[0] == "校友" and len(info) == 1

            if (len(info) == 2 and (is_bachelor or is_master or is_phd)) or is_alumi:
                info.append(mtext[1:])
                print(info)
            elif info[0] in ["碩士", "博士", "學士"]:
                info = [info[0], info[1], mtext[1:]]
            elif info[0] == "校友":
                info = [info[0], mtext[1:]]

            user_id_label_dict[user_id] = info
            message = labeling_intention(
            ) if info[0] == "校友" else labeling_know_from()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@校友":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_academic_group_alumi()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@一般民眾":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_intention()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@演講，研討會", "@覓食", "@參加營隊", "@場地使用", "@休憩", "@其它"]:
        try:
            action_kind = "貼標"
            info = user_id_label_dict[user_id]
            is_alumi = (
                len(info) == 2
                and info[0] == "校友"
                and info[1] in ["人社法商管", "生物醫藥護", "科學理工"]
            )
            if info == ["一般民眾"] or is_alumi:
                info.append(mtext[1:])
            elif info[0] == "校友":
                info = [info[0], info[1], mtext[1:]]
            elif info[0] == "一般民眾":
                info = [info[0], mtext[1:]]

            user_id_label_dict[user_id] = info
            message = labeling_know_from()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@教職員":
        try:
            action_kind = "貼標"
            user_id_label_dict[user_id] = [mtext[1:]]
            message = labeling_service_unit()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@學院系所", "@行政單位"]:
        try:
            action_kind = "貼標"
            info = user_id_label_dict[user_id]
            if info == ["教職員"]:
                info.append(mtext[1:])
            elif info[0] == "教職員":
                info = [info[0], mtext[1:]]
            user_id_label_dict[user_id] = info
            message = labeling_know_from()
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext in ["@親友分享", "@LINE查詢", "@校內宣傳", "@網路搜尋", "@LINE橫幅廣告"]:
        try:
            action_kine = "貼標"
            info = user_id_label_dict[user_id]
            info.append(mtext[1:])
            
            if info[0] in ["學士", "碩士", "博士"]:
                info = ["在校生"] + info

            message = [
                TextSendMessage(
                    f'您的選擇是：\n{"/".join(info)}\n\n若無須更改，請按下「開始使用」'),
                labeling_confirm(),
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@開始使用":
        try:
            action_kind = "貼標"
            if user_id not in user_id_label_dict.keys():
                message = [
                    TextSendMessage("抱歉，小幫手沒有記錄到您之前的選項，麻煩您再選一次!"),
                    labeling_character(),
                ]
            else:
                if user_id_label_dict[user_id][0] in ["學士", "碩士", "博士"]:
                    user_id_label_dict[user_id] = ["在校生"] + user_id_label_dict[user_id]
                    
                label_str = "/".join(user_id_label_dict[user_id][:-1])
                print(label_str)
                know_from = user_id_label_dict[user_id][-1]
                query = f"insert into 分眾貼標 (user_id, label, know_from, create_time, language) values ('{user_id}', '{label_str}', '{know_from}', '{now_time}', 'chinese')"
                cnxn.cursor().execute(query)
                cnxn.cursor().commit()

                del user_id_label_dict[user_id]
                message = [TextSendMessage(
                    f"耶~恭喜你完成！\n點選畫面下方的選單圖示，或是直接輸入問題，就可以獲得想要的資訊喔！"
                )]
# 112上學期開學集點抽獎活動===============================================

                # message = add_activity_info(message)

# ===================================================================
                if datetime.datetime.now().month in range(2, 8):
                    link_richmenu_to_user(S_HALF_RICHMENU_FILE, user_id)
                else:
                    link_richmenu_to_user(F_HALF_RICHMENU_FILE, user_id)

            line_bot_api.reply_message(event.reply_token, message)
        except Exception as err:
            print(err)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext == "@校園安全SOP":
        try:
            action_kind = mtext[1:]
            message = campus_security_sop()
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            print(e)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
        pass
    elif mtext in ["@性平事件處理要點", "@詐騙事件處理要點", "@遺失事件處理要點", "@車禍事件處理要點"]:
        try:
            action_kind = mtext[1:]
            images = {
                "@性平事件處理要點": "https://i.imgur.com/9LuUC3Q.png",
                "@詐騙事件處理要點": "https://i.imgur.com/H4BiIq0.png",
                "@遺失事件處理要點": "https://i.imgur.com/SsaQGQi.png",
                "@車禍事件處理要點": "https://i.imgur.com/QLdorJb.png"
            }
            message = ImageSendMessage(
                original_content_url=images[mtext],
                preview_image_url=images[mtext]
            )
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
            print(e)
    elif mtext == "@重新選擇":
        try:
            action_kine = "貼標"
            if user_id in user_id_label_dict.keys():
                del user_id_label_dict[user_id]
                
            message = labeling_main()
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as err:
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)
    elif mtext[0] == "#":
        action_kind = "常見QA"
        message = []
        for title in QA_title["title"]:
            if mtext == "#" + title:
                try:
                    message = QnA_Selection(title, detail_Flag, detail_request)
                    line_bot_api.reply_message(event.reply_token, message)
                except:
                    message = TextSendMessage(text="發生錯誤！")
                    line_bot_api.reply_message(event.reply_token, message)
                break
            if "#" + title + "#" in mtext:
                try:
                    answer = pd.read_sql(
                        "SELECT answer FROM QnA WHERE bot_id=1 AND title='"
                        + title
                        + "' AND question='"
                        + mtext[mtext.find("-") + 1:]
                        + "'",
                        cnxn,
                    )["answer"][0]
                    message = TextSendMessage(text=answer)
                    line_bot_api.reply_message(event.reply_token, message)
                except:
                    message = TextSendMessage(text="發生錯誤！")
                    line_bot_api.reply_message(event.reply_token, message)
                break

    elif mtext[0] == "✦":
        message = []
        if mtext[len(mtext) - 1] == "✦":
            try:
                action_kind = "位置資訊"
                message = dep_detail_info(mtext[: len(mtext) - 1])
                line_bot_api.reply_message(event.reply_token, message)
            except:
                message = TextSendMessage(text="發生錯誤！")
                line_bot_api.reply_message(event.reply_token, message)
        else:
            for unit in all_unit["單位"]:
                if mtext == "✦" + unit:
                    try:
                        action_kind = "位置資訊"
                        message = dep_button(unit, "交通")
                        line_bot_api.reply_message(event.reply_token, message)
                    except:
                        message = TextSendMessage(text="發生錯誤！")
                        line_bot_api.reply_message(event.reply_token, message)
                    break
    elif mtext[0] == "★":
        message = []
        if mtext[len(mtext) - 1] == "★":
            try:
                action_kind = "位置資訊"
                message = dep_detail_info(mtext[: len(mtext) - 1])
                line_bot_api.reply_message(event.reply_token, message)
            except:
                message = TextSendMessage(text="發生錯誤！")
                line_bot_api.reply_message(event.reply_token, message)
        else:
            for unit in y_all_unit["單位"]:
                if mtext == "★" + unit:
                    try:
                        action_kind = "位置資訊"
                        message = dep_button(unit, "陽明")
                        line_bot_api.reply_message(event.reply_token, message)
                    except:
                        message = TextSendMessage(text="發生錯誤！")
                        line_bot_api.reply_message(event.reply_token, message)
                    break
    elif len(mtext) < 500:
        try:
            intent = mtext.split("/")[0]
            question_feedback_intent = mtext.split("(|)")[0]
            message_flag = True
            comment = (
                "SELECT TOP(1) action FROM action_record WHERE bot_id=1 AND [user_id]='"
                + user_id
                + "' ORDER BY time DESC"
            )
            # 若為問題回報
            _question = pd.read_sql(comment, cnxn)["action"]
            if len(_question) != 0 and _question[0] == "@問題回饋":
                # dataframe欄位  user_id:nvarchar(50), time:nvarchar(50), bot_id:int(1為校務資訊),suggestion:nvarchar(50)
                action_kind = "問題回饋"
                suggest_flag = True
                d = {
                    "user_id": [user_id],
                    "time": [now_time],
                    "bot_id": [1],
                    "suggestion": [origin_mtext],
                }
                table = pd.DataFrame(data=d)
                # *** engine 修改 ***
                query = (
                    "insert into user_suggestion (user_id, time, bot_id,suggestion) values ('"
                    + user_id
                    + "','"
                    + now_time
                    + "',1,'"
                    + origin_mtext
                    + "')"
                )
                cnxn.cursor().execute(query)
                cnxn.cursor().commit()
                message = TextSendMessage(text="您的寶貴意見是我們改進的動力，謝謝您的回饋!")
            # 新生專區/社團活動
            elif intent == "社團活動" or intent == "@社團活動": #按鈕
                action_kind = "社團活動"
                message = club_activity(mtext, user_id)
            # 位置資訊
            elif intent == "@查詢教室、處室位置" or intent == "查詢教室、處室位置": 
                action_kind = "位置資訊"
                message = get_location_info(mtext, user_id)
            # 課程相關
            elif intent == "課程種類一覽": 
                action_kind = "教務資訊"
                message = show_course(mtext, user_question)
            elif intent == "免修申請":    #有問題
                action_kind = "教務資訊"
                message = course_exemption(mtext, user_question)
            elif intent == "免擋修申請":  
                action_kind = "教務資訊"
                message = no_block_course(mtext, user_question)
            elif intent == "考古題相關":  
                action_kind = "教務資訊"
                message = archaeological_question(
                    mtext, user_question, user_id)
            # 系所畢業相關資格規定
            elif intent == "系所畢業資格" or intent == "@系所畢業規定": #有問題
                action_kind = "教務資訊"
                message = graguated_information(mtext, user_id)
            elif intent == "口試及離校手續" or intent == "修課年限": #有問題
                action_kind = "教務資訊"
                message = graguated_information(mtext, user_id)
            # 各系所申請入學相關
            elif intent == "各系所申請報名方式": #有問題
                action_kind = "教務資訊"
                message = academy_admission(mtext, user_id)
            # 獎助學金申請
            # elif intent == '獎學金申請':  #有問題
            # action_kind="獎學金"
            # message = scholarship(mtext)
            # 學分抵免相關
            elif intent == "修課規定":
                action_kind = "教務資訊"
                message = course_rule(mtext, user_id)
            elif intent == "系所學分抵免規定" or intent == "@系所學分抵免規定":
                action_kind = "教務資訊"
                message = credits_waiver_and_transference(mtext, user_id)
            elif intent == "@上修學分認定" or intent == "上修學分認定":
                action_kind = "教務資訊"
                message = credits_waiver_and_transference(mtext, user_id)
            elif intent == "@下修學分認定" or intent == "@下修學分認定":
                action_kind = "教務資訊"
                message = credits_waiver_and_transference(mtext, user_id)
            elif intent == "預修學分抵免" or intent == "@學分認定":   #有問題 人社系
                action_kind = "教務資訊"
                message = credits_waiver_and_transference(mtext, user_id)
            elif intent == "@預修學分抵免" or intent == "@學分認定":  #有問題 人社系
                action_kind = "教務資訊"
                message = credits_waiver_and_transference(mtext, user_id)
            elif intent == "@詢問學分抵免規定":    
                action_kind = "教務資訊"
                message = ask_credits_waiver_and_transference(mtext)
            # 各單位簡介
            elif intent == "各單位簡介或功能" or intent == "@各單位簡介或功能":
                action_kind = "教務資訊"
                message = introduction_of_department(mtext)
            elif intent == "@歷史沿革" or intent == "各單位的歷史或沿革":
                action_kind = "教務資訊"
                message = history_of_department(mtext, user_question)
            elif intent == "@未來出路" or intent == "系所未來出路":
                action_kind = "教務資訊"
                message = future_of_department(mtext, user_question)
            elif intent == "@指導教授":  
                action_kind = "教務資訊"
                message = professer_of_department(mtext)
            elif intent == "@教授選定" or intent == "如何選定指導教授": 
                action_kind = "教務資訊"
                message = professor_choose(mtext, user_question)
            elif intent == "@教授共指" or intent == "共同指導相關規定": 
                action_kind = "教務資訊"
                message = professor_joint(mtext, user_question)
            elif intent == "@教授更換" or intent == "如何更換指導教授": 
                action_kind = "教務資訊"
                message = professor_change(mtext, user_question)
            elif intent == "推薦信相關" or intent == "@推薦信":        
                action_kind = "教務資訊"
                message = recommendation(mtext, user_question)
            # 各式證明申請
            elif intent == "證明申請": #有問題 入台證
                action_kind = "教務資訊"
                message = proof(mtext, user_question)
            elif intent == "@停車證明": #原luis沒有這個intent 404error
                message = parking_regist(mtext)
            # 校內單位工讀、徵才相關機會
            elif intent == "工讀機會":
                action_kind = "工讀資訊"
                message = job()
            # 圖書館相關規定
            elif intent == "圖書館相關規定" or intent == "@圖書館相關規定":
                action_kind = "校園資訊"
                message = library(mtext)
            elif intent == "@圖書館營業時間": 
                action_kind = "場館營業時間"
                message = library_hours(mtext)
            elif intent == "@圖書館借還書":  
                action_kind = "場館營業時間"
                message = library_detail_behavior(mtext)
            # 能租借之場地或設備一覽
            elif intent == "能租借之場地或設備一覽" or intent == "@能租借之場地或設備一覽":
                action_kind = "校園資訊"
                message = place_object_borrow(mtext, user_id)
            elif intent == "@租借方式": 
                action_kind = "校園資訊"
                message = how_to_borrow(mtext)
            elif intent == "@場地物品詳細資訊":
                action_kind = "校園資訊"
                message = place_object_detial(mtext)
            # 地圖
            elif intent == "校區地圖": #有問題
                action_kind = "位置資訊"
                message = campus_map(mtext)
            elif intent == "@校園地圖":
                action_kind = "位置資訊"
                message = button_place_information()
            # 門診資訊
            elif intent == "@校園門診資訊":
                action_kind = "校園資訊"
                message = campus_clinic(mtext)
            # 服務學習相關問題
            elif intent == "@服務學習資訊":
                action_kind = "校園資訊"
                message = service_learning(mtext)
            # 學生社團相關問題
            elif intent == "@學生社團資訊":
                action_kind = "校園資訊"
                message = club(mtext)
            # 宿舍相關問題
            elif intent == "@宿舍服務資訊":
                action_kind = "校園資訊"
                message = dormitory_service(mtext)
            elif intent == "@宿舍申請資訊":
                action_kind = "校園資訊"
                message = dormitory_applyment(mtext)
            elif intent == "@宿舍搬遷資訊":
                action_kind = "校園資訊"
                message = dormitory_transfer(mtext)
            elif intent == "@宿舍退宿資訊":
                action_kind = "校園資訊"
                message = dormitory_resignment(mtext)
            elif intent == "@宿舍規定資訊":
                action_kind = "校園資訊"
                message = dormitory_rule(mtext)
            # 游泳館體育館人數
            elif intent == "健身房人數" or intent == "游泳池人數":
                action_kind = "校園資訊"
                message = gym_base()
            # 學生餐廳
            elif intent == "餐廳營業時間" or intent == "@學餐資訊":
                action_kind = "學餐資訊"
                message = restaurant(mtext)
            # elif intent == "@詢問學生餐廳":
            #     action_kind = "學餐資訊"
            #     message = ask_restaurant(mtext, user_question)
            # 門禁卡申請
            elif intent == "門禁卡申請" or intent == "@門禁卡申請":
                action_kind = "校園資訊"
                message = building_access(mtext, user_question, user_id)
            # 校園ATM
            elif intent == "@校園ATM":
                action_kind = "位置資訊"
                message = atm_location(mtext, user_question)
            # 校園AED
            elif intent == "@校園AED地圖" or intent == "@校內AED地圖":
                action_kind = "位置資訊"
                message = aed_location(mtext, user_question)
            # 校內公車查詢
            elif intent == "校內公車查詢":
                action_kind = "交通資訊"
                message = bus_search(mtext)
            # You-Bike
            elif intent == "@YouBike資訊":
                action_kind = "交通資訊"
                message = [
                    # removed imgur image links in favor of google drive
                    ImageSendMessage(
                        # original_content_url="https://imgur.com/L9C1TxF.jpg",
                        # preview_image_url="https://imgur.com/L9C1TxF.jpg",
                        original_content_url="https://drive.google.com/file/d/1CrSOu3-Q6hdt_ZjzrLfUWhJjVXQ1PQxj/view?usp=sharing",
                        preview_image_url="https://drive.google.com/file/d/1CrSOu3-Q6hdt_ZjzrLfUWhJjVXQ1PQxj/view?usp=sharing",
                    ),
                    ImageSendMessage(
                        # original_content_url="https://imgur.com/wQI0qvb.jpg",
                        # preview_image_url="https://imgur.com/wQI0qvb.jpg",
                        original_content_url="https://drive.google.com/file/d/12cPR-6G-tnTzGyX2jJHaoLcSnjnOh9ds/view?usp=sharing",
                        preview_image_url="https://drive.google.com/file/d/12cPR-6G-tnTzGyX2jJHaoLcSnjnOh9ds/view?usp=sharing",
                    ),
                    UBIKE(),
                ]
            # 結束對話
            elif intent == "@結束":
                message = TextSendMessage("此對話已結束，可以重新開始跟小幫手對話囉！")

            # 答案回饋
            elif question_feedback_intent == "@答案回饋":
                message = answer_feedback(mtext, user_id)

            else:
                message = interview_information(mtext)

            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            print(e)
            message = TextSendMessage(text="發生錯誤！")
            line_bot_api.reply_message(event.reply_token, message)

    # ==============================================================================================================================

    if len(origin_mtext) > 45:
        origin_mtext = origin_mtext[0:45] + "..."
    d = {
        "user_id": [user_id],
        "time": [now_time],
        "bot_id": [1],
        "action_kind": [action_kind],
        "action": [mtext],
    }
    table = pd.DataFrame(data=d)
    # *** engine 修改 ***
    query = (
        "insert into action_record (user_id, time, bot_id,action_kind,action,origin_text,origin_kind) values ('"
        + user_id
        + "','"
        + now_time
        + "',1,'"
        + action_kind
        + "','"
        + mtext
        + "','"
        + origin_mtext
        + "','"
        + origin_kind
        + "')"
    )
    print(query)
    cnxn.cursor().execute(query)
    cnxn.cursor().commit()
    
    if isinstance(message, list) or isinstance(message, tuple):
        for ele in message:
            message_parse(ele, user_id, now_time, origin_mtext, research_type)
    else:
        message_parse(message, user_id, now_time, origin_mtext, research_type)


# 測試PostbackEvent，未來想要大改=======================================================================================


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data_path = event.postback.data
    intent = data_path.split("/")[0] if data_path[:2] != "¥#" else data_path
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    origin_kind = "按鈕選擇"
    research_type = 0
    message = None

    _ = ask_detail("", user_id)  # 更新資料庫用

    print(f"INTENT: {intent}")
    try:
        # 各系所申請入學相關
        if intent == "@系所申請" or intent == "五年碩與逕博規定":
            action_kind = "教務資訊"
            message = regular_admission(data_path, user_id)
        elif intent == "@入學方式":
            action_kind = "教務資訊"
            message = department_admission(data_path)
        elif intent == "@五年碩申請方式":
            action_kind = "教務資訊"
            message = five_years_master_degree_admission(data_path)
        elif intent == "@逕博申請方式":
            action_kind = "教務資訊"
            message = doctor_admission(data_path)
        elif intent == "@輔系與雙主修":
            action_kind = "教務資訊"
            message = aux_and_double_major_admission(data_path)
        elif intent == "@輔系申請" or intent == "輔修申請":
            action_kind = "教務資訊"
            message = aux_admission(data_path, user_id)
        elif intent == "@輔系申請規定":
            action_kind = "教務資訊"
            message = aux_admission_information(data_path)
        elif intent == "@雙主修申請" or intent == "雙主修申請":
            action_kind = "教務資訊"
            message = double_major_admission(data_path, user_id)
        elif intent == "@雙主修申請規定":
            action_kind = "教務資訊"
            message = double_major_admission_information(data_path)
        elif intent == "@轉換系所" or intent == "轉換系所":
            action_kind = "教務資訊"
            message = transfer_department_admission(data_path, user_id)
        elif intent == "@轉入系所":
            action_kind = "教務資訊"
            message = transfer_department_in(data_path)
        elif intent == "@轉出系所":
            action_kind = "教務資訊"
            message = transfer_department_out(data_path)
        elif intent == "@雙聯學位" or intent == "雙聯學位申請":
            action_kind = "教務資訊"
            message = double_degree_admission(data_path, user_id)
        elif intent == "@雙聯學位申請規定":
            action_kind = "教務資訊"
            message = double_degree_admission_information(data_path)
        # 系所畢業相關資格規定
        elif intent == "系所畢業資格" or intent == "@系所畢業規定":
            action_kind = "教務資訊"
            message = graguated_information(data_path, user_id)
        elif intent == "口試及離校手續" or intent == "修課年限":
            action_kind = "教務資訊"
            message = graguated_information(data_path, user_id)
        elif intent == "@詢問畢業規定":
            action_kind = "教務資訊"
            message = ask_graguated_information(data_path)
        elif intent == "修課規定":
            action_kind = "教務資訊"
            message = course_rule(data_path, user_id)
        elif intent == "系所學分抵免規定" or intent == "@系所學分抵免規定":
            action_kind = "教務資訊"
            message = credits_waiver_and_transference(data_path, user_id)
        elif intent == "上修學分認定" or intent == "下修學分認定":
            action_kind = "教務資訊"
            message = credits_waiver_and_transference(data_path, user_id)
        elif intent == "@上修學分認定" or intent == "@下修學分認定":
            action_kind = "教務資訊"
            message = credits_waiver_and_transference(data_path, user_id)
        elif intent == "預修學分抵免" or intent == "學分認定":
            action_kind = "教務資訊"
            message = credits_waiver_and_transference(data_path, user_id)
        elif intent == "@預修學分抵免" or intent == "@學分認定":
            action_kind = "教務資訊"
            message = credits_waiver_and_transference(data_path, user_id)
        elif intent == "@詢問學分抵免規定":
            action_kind = "教務資訊"
            message = ask_credits_waiver_and_transference(data_path)
        # 英文版
        elif intent[0] == '¥':
            try:
                mtext = intent[1:]
                action_kind, message = handle_english_postback_event(mtext, user_id, cnxn, now_time)
            except:
                message = TextSendMessage(text="An unexpected error occurred.")
        #switch language
        elif intent == "to_english":
            action_kind = "變更語言"

            link_richmenu_to_user(ENG_RICHMENU_FILE, user_id)
            
            query = f"""
                BEGIN TRANSACTION;
                DELETE FROM user_language WHERE user_id = '{user_id}';
                INSERT INTO user_language (user_id, current_language) VALUES ('{user_id}', 'english');
                COMMIT;
            """
            cnxn.cursor().execute(query)
            cnxn.commit()
        elif intent == "to_chinese":
            action_kind = "變更語言"

            if datetime.datetime.now().month in range(2, 8):
                link_richmenu_to_user(S_HALF_RICHMENU_FILE, user_id)
            else:
                link_richmenu_to_user(F_HALF_RICHMENU_FILE, user_id)
            
            query = f"""
                BEGIN TRANSACTION;
                DELETE FROM user_language WHERE user_id = '{user_id}';
                INSERT INTO user_language (user_id, current_language) VALUES ('{user_id}', 'chinese');
                COMMIT;
            """
            cnxn.cursor().execute(query)
            cnxn.commit()
                
        if message != None:
            line_bot_api.reply_message(event.reply_token, message)
    except:
        message = TextSendMessage(text="發生錯誤！")
        line_bot_api.reply_message(event.reply_token, message)

    if message != None or intent.startswith('to_'):
        if len(data_path) > 45:
            data_path = data_path[0:45] + "..."
        # *** engine 修改 ***
        query = (
            "insert into action_record (user_id, time, bot_id,action_kind,action,origin_text,origin_kind) values ('"
            + user_id
            + "','"
            + now_time
            + "',1,'"
            + action_kind
            + "','"
            + data_path
            + "','"
            + data_path
            + "','"
            + origin_kind
            + "')"
        )
        print(query)
        cnxn.cursor().execute(query)
        cnxn.cursor().commit()

        if isinstance(message, list) or isinstance(message, tuple):
           for ele in message:
               message_parse(ele, user_id, now_time, data_path, research_type)
        elif action_kind != '變更語言':
           message_parse(message, user_id, now_time, data_path, research_type)


# ==================================================================================================================================


def message_parse(message_obj, user_id, now_time, origin_mtext, research_type):
    research_notunderstand = 0
    research_chatbot_response = ""
    research_dialog_answer = 1
    if isinstance(message_obj, ImageSendMessage):
        research_chatbot_response += "圖片回覆"
        # print("Image")
    elif isinstance(message_obj, LocationSendMessage):
        research_chatbot_response += "地址回覆"
        # print("Location")
    elif str((message_obj.type)) == "template":
        if hasattr(message_obj.template, "columns"):  # 橫向多個表單
            count = 0
            for ele in message_obj.template.columns:
                count = count + 1
                try:
                    research_chatbot_response += " " + \
                        str(count) + ". " + ele.title
                except Exception:
                    research_chatbot_response += (
                        " " + str(count) + ". " + str(type(ele))
                    )
                
                # print()
                # print(ele.text)
                # print()
                # print(ele.title)
                # for eles in ele.actions:
                #     print()
                #     print(eles.label)
        else:  # 單個垂直表單
            research_chatbot_response += message_obj.template.title
            count = 0
            for ele in message_obj.template.actions:
                count = count + 1
                try:
                    research_chatbot_response += str(count) + "." + ele.label
                except AttributeError:
                    research_chatbot_response += str(count) + \
                        "." + str(type(ele))
            # print()
            # print(message_obj.template.text)
            # print()
            # print(message_obj.template.title)
            # for ele in message_obj.template.actions:
            #     print()
            #     print(ele.label)
    elif str((message_obj.type)) == "text":  # 單個文字訊息
        research_chatbot_response += message_obj.text
        if message_obj.text.find("小幫手無法辨識") != -1:
            research_notunderstand = 1
            research_dialog_answer = 0
        elif message_obj.text.find("發生錯誤") != -1:
            research_dialog_answer = 0
        # print()
        # print(message_obj.text)
    tmp = ""
    for ele in research_chatbot_response.split(" "):
        if ele == " ":
            continue
        else:
            tmp += ele
    tmp2 = ""
    for ele in tmp.split("\n"):
        tmp2 += ele + " "
    research_chatbot_response = (
        tmp2.replace("@", "")
        .replace("/", " ")
        .replace(";", "")
        .replace("'", "")
        .replace("-", "")
        .strip()
    )
    tmp = ""
    for ele in origin_mtext.split(" "):
        if ele == " ":
            continue
        else:
            tmp += ele
    tmp2 = ""
    for ele in tmp.split("\n"):
        tmp2 += ele + " "
    origin_mtext = (
        tmp2.replace("@", "")
        .replace("/", " ")
        .replace(";", "")
        .replace("'", "")
        .strip()
    )
    research_chatbot_response = (
        research_chatbot_response[:100]
        if len(research_chatbot_response) > 100
        else research_chatbot_response
    )
    query = "insert into dialog_logs (user_id, time, type, notunderstand, dialog_answer, user_input, chatbot_response) values"
    query = (
        query
        + "('"
        + user_id
        + "','"
        + now_time
        + "',"
        + str(research_type)
        + ",'"
        + str(research_notunderstand)
        + "','"
        + str(research_dialog_answer)
        + "','"
        + origin_mtext
        + "','"
        + research_chatbot_response
        + "')"
    )
    print(query)
    cnxn.cursor().execute(query)
    cnxn.cursor().commit()

    return


def share():
    print("get@分享帳號")
    message = TemplateSendMessage(
        alt_text="NONE",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://i.imgur.com/AHk16Lc.png",
                    title="幫忙分享小幫手吧",
                    text="點選下面按鈕推薦給好友或直接讓好友掃描 QR code加入",
                    actions=[
                        # MessageTemplateAction(label='防疫公告',text ='@防疫公告')
                        URITemplateAction(
                            label="分享給好友", uri="line://nv/recommendOA/@432ejleo"
                        )
                    ],
                )
            ]
        ),
    )
    return message


def QnA_Selection(title, detail_Flag, detail_request):
    if detail_Flag:
        QA_selection = pd.read_sql(
            "SELECT question FROM QnA WHERE title='"
            + title
            + "' AND question LIKE '%"
            + detail_request
            + "%' AND bot_id=1",
            cnxn,
        )
    else:
        QA_selection = pd.read_sql(
            "SELECT question FROM QnA WHERE title='" + title + "' AND bot_id=1", cnxn
        )
    col = []
    for question in QA_selection["question"]:
        col.append(
            CarouselColumn(
                title=question,
                text=" ",
                actions=[
                    MessageTemplateAction(
                        label="簡短回答", text="#" + title + "#\n -" + question
                    )
                ],
            )
        )
    message = TemplateSendMessage(
        alt_text="NONE", template=CarouselTemplate(columns=col)
    )
    return message

def button_place_information():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="校園資訊",
            text="請選取所需服務",
            actions=[
                MessageTemplateAction(
                    # label = "各處室位置分機",
                    # text = "@各處室位置分機"
                    label="查詢教室、處室位置",
                    text="@查詢教室、處室位置/沒指定",
                ),
                MessageTemplateAction(label="校內AED地圖", text="@校內AED地圖"),
                MessageTemplateAction(label="校區地圖", text="@校區地圖"),
                MessageTemplateAction(label="停車地圖", text="@停車地圖")
                # 因為 LINE 只能放四個訊息，所以暫時把看起來比較不需要的分機位置換掉
                # ,
                # MessageTemplateAction(
                #    label = "各處室位置分機",
                #    text = "@各處室位置分機"
                # )
            ],
        ),
    )

    return message


def abroad():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="國際交換",
            text="請選取所需服務",
            actions=[
                MessageTemplateAction(label="交換申請公告", text="@交換申請公告"),
                MessageTemplateAction(label="可交換列表", text="@可交換列表"),
                MessageTemplateAction(label="申請說明會簡報", text="@申請說明會簡報"),
                MessageTemplateAction(label="交換獎學金", text="@交換獎學金"),
            ],
        ),
    )

    return message


def button_school_information():
    message1 = TemplateSendMessage(
        alt_text="NONE",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title="行事曆",
                    text="前往行事曆網站",
                    actions=[
                        URITemplateAction(
                            label="NYCU行事曆", uri="https://www.nycu.edu.tw/calendar/"
                        )
                    ],
                ),
                CarouselColumn(
                    title="校園公告",
                    text="查看最新學校公告",
                    actions=[MessageTemplateAction(
                        label="點選查閱", text="@重要公告")],
                ),
                CarouselColumn(
                    title="校內工讀",
                    text="查閱最新工讀資訊",
                    actions=[MessageTemplateAction(label="點選查找", text="工讀")],
                ),
                CarouselColumn(
                    title="健身房人數",
                    text="查閱即時健身房人數",
                    actions=[MessageTemplateAction(label="點選查找", text="@健身房")],
                ),
            ]
        ),
    )
    message2 = TemplateSendMessage(
        alt_text="NONE",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title="場館營業時間",
                    text="查看各場館營業時間",
                    actions=[MessageTemplateAction(
                        label="點選查找", text="@場館營業時間")],
                ),
                CarouselColumn(
                    title="餐廳菜單",
                    text="查閱學餐菜單",
                    actions=[MessageTemplateAction(label="點選查找", text="餐廳")],
                ),
                CarouselColumn(
                    title="常見Q&A",
                    text="各式校園相關資訊問答",
                    actions=[MessageTemplateAction(
                        label="點選閱覽", text="@常見Q&A")],
                ),
                CarouselColumn(
                    title="分享帳號",
                    text="分享給身邊好友",
                    actions=[MessageTemplateAction(label="分享", text="@分享帳號")],
                ),
            ]
        ),
    )
    message = [message1, message2]
    return message

# UNUSED
# def button_medicine():
#     message = TemplateSendMessage(
#         alt_text="NONE",
#         template=ButtonsTemplate(
#             title="校園門診資訊",
#             text="請選取校區",
#             actions=[
#                 URITemplateAction(
#                     label="交大校區", uri="https://health.sa.nctu.edu.tw/?page_id=533"
#                 ),
#                 URITemplateAction(
#                     label="陽明校區", uri="https://hc.ym.edu.tw/files/11-1205-19.php"
#                 ),
#             ],
#         ),
#     )
#     return message


# google drive preview link
# https://drive.google.com/uc?id=1epodtBeKWLCeCYMS23M6QyFh9ZUHHYLW&export=view
def traffic_image_map(mtext):
    message = ImagemapSendMessage(
        # base_url = "https://i.imgur.com/5qcMhUr.png",
        base_url="https://i.imgur.com/5qcMhUr.png",
        alt_text=mtext,
        base_size=BaseSize(width=1040, height=1040),
        actions=[
            MessageImagemapAction(
                text="@校區間校車",
                area=ImagemapArea(x=80, y=175, width=240, height=355),
            ),
            MessageImagemapAction(
                text="@陽明校區內校車",
                area=ImagemapArea(x=410, y=175, width=240, height=355),
            ),
            MessageImagemapAction(
                text="@光復 <=> 火車站",
                area=ImagemapArea(x=740, y=175, width=240, height=355),
            ),
            MessageImagemapAction(
                text="@YouBike資訊",
                area=ImagemapArea(x=80, y=600, width=240, height=355),
            ),
            MessageImagemapAction(
                text="@豪泰客運",
                area=ImagemapArea(x=410, y=600, width=240, height=355),
            ),
            MessageImagemapAction(
                text="@小紅巴",
                area=ImagemapArea(x=740, y=600, width=240, height=355),
            ),
        ]
    )
    return message


def button_travel(mtext):
    message = TemplateSendMessage(
        alt_text=mtext,
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title="校區間校車",
                    text="光復校區<=>陽明、博愛、客院(高鐵站)",
                    actions=[MessageTemplateAction(
                        label="點選查看", text="@校區間校車")],
                ),
                CarouselColumn(
                    title="陽明校區內校車",
                    text="綠線、紅線、559路公車",
                    actions=[MessageTemplateAction(
                        label="點選查看", text="@陽明校區內校車")],
                ),
                CarouselColumn(
                    title="光復校區2路公車",
                    text="光復校區<=>新竹火車站",
                    actions=[MessageTemplateAction(
                        label="點選查看", text="@光復 <=> 火車站")],
                ),
                CarouselColumn(
                    title="YouBike",
                    text="校園內YouBike即時狀態",
                    actions=[MessageTemplateAction(
                        label="點選查看", text="@YouBike資訊")],
                ),
                CarouselColumn(
                    title="豪泰客運",
                    text="台北轉運<=>光復校區",
                    actions=[MessageTemplateAction(
                        label="點選查看", text="@豪泰客運")],
                ),
                CarouselColumn(
                    title="小紅巴",
                    text="新竹園區公車",
                    actions=[MessageTemplateAction(label="點選查看", text="@小紅巴")],
                ),
            ]
        ),
    )
    return message


def button_school_map():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/dyEyhU0.png",
                    action=MessageTemplateAction(label="光復校區", text="@光復校區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QDGaBZi.jpg",
                    action=MessageTemplateAction(label="陽明校區", text="@陽明校區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/hujyiJG.jpg",
                    action=MessageTemplateAction(label="博愛校區", text="@博愛校區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/zdbNQvp.jpg",
                    action=MessageTemplateAction(label="六家校區", text="@六家校區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Serg3SB.png",
                    action=MessageTemplateAction(label="台北校區", text="@台北校區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/gsbNGsl.png",
                    action=MessageTemplateAction(label="蘭陽院區", text="@蘭陽院區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/t0WBzGS.png",
                    action=MessageTemplateAction(label="新民院區", text="@新民院區"),
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/vKejQtr.png",
                    action=MessageTemplateAction(label="台南校區", text="@台南校區"),
                ),
            ]
        ),
    )
    return message


def button_school_parking_map():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://imgur.com/0DypDzl.jpg",
                    action=MessageTemplateAction(
                        label="光復校區停車地圖", text="@光復校區停車地圖"),
                ),
                ImageCarouselColumn(
                    image_url="https://imgur.com/W6rJJR2.jpg",
                    action=MessageTemplateAction(
                        label="陽明校區停車地圖", text="@陽明校區停車地圖"),
                ),
            ]
        ),
    )
    return message


def button_healthy_imformation():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="健康資訊",
            text="請選取所需服務",
            actions=[
                MessageTemplateAction(label="校內門診時間", text="@校內門診時間"),
                MessageTemplateAction(label="學校附近醫療院所", text="@學校附近醫療院所"),
                MessageTemplateAction(label="AED位置分布地圖", text="@AED位置分布地圖"),
            ],
        ),
    )
    return message

# DEPRECATED
# def QA_first_layer():
#     message = TemplateSendMessage(
#         alt_text="NONE",
#         template=ButtonsTemplate(
#             title="常見Q&A",
#             text="請選擇校區",
#             actions=[
#                 MessageTemplateAction(label="交大校區", text="@常見Q&A(交大校區)"),
#                 MessageTemplateAction(label="陽明校區", text="@常見Q&A(陽明校區)"),
#             ],
#         ),
#     )
#     return message


def button_QA_NYCU():
    QA_c = [
        CarouselColumn(
            title="宿舍申請(陽明校區)",
            text="Q&A",
            actions=[
                URITemplateAction(
                    label="宿舍申請(陽明校區)", uri="https://osa.nycu.edu.tw/osa/ch/app/folder/3716"
                )
            ],
        )
    ]
    for title in QA_title["title"]:
        QA_c.append(
            CarouselColumn(
                title=title,
                text="Q&A",
                # temporary fix for scholarship thing
                actions=[MessageTemplateAction(label=title, text="#" + title)]
                if title != "獎學金申請"
                else [MessageTemplateAction(label=title, text="@有哪些獎學金+申請流程")],
            )
        )
    message = TemplateSendMessage(
        alt_text="NONE", template=CarouselTemplate(columns=QA_c)
    )
    return message


def button_recent_activities():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="近期活動",
            text="請選取所需服務",
            actions=[
                MessageTemplateAction(label="演講/研討會", text="@演講/研討會"),
                MessageTemplateAction(label="體育活動", text="@體育活動"),
                MessageTemplateAction(label="藝文展演", text="@藝文展演"),
                MessageTemplateAction(label="市府藝文活動", text="@市府藝文活動"),
            ],
        ),
    )
    return message


# 工讀
def all_jobs():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="工讀資訊",
            text="請選取項目",
            actions=[
                MessageTemplateAction(label="一般徵才", text="@一般徵才"),
                MessageTemplateAction(label="家教資訊", text="@家教資訊"),
            ],
        ),
    )
    return message


# 場館營業時間
def opening_hours():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="場館營業時間",
            text="請選擇校區",
            actions=[
                MessageTemplateAction(label="陽明校區", text="@陽明校區場館營業時間"),
                MessageTemplateAction(label="光復校區", text="@光復校區場館營業時間"),
            ],
        ),
    )
    return message


def opening_hours_ym():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="陽明校區場館營業時間",
            text="請選取項目",
            actions=[
                MessageTemplateAction(label="圖書館", text="@圖書館營業時間/陽明校區"),
                MessageTemplateAction(
                    label="球館及球場營業時間", text="@球館及球場營業時間(陽明校區)"),
                MessageTemplateAction(label="游泳健身館", text="@游泳健身館營業時間"),
                MessageTemplateAction(label="其他運動場館", text="@其他運動場館營業時間"),
            ],
        ),
    )
    return message


def opening_hours_ct():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="光復校區場館營業時間",
            text="請選取項目",
            actions=[
                MessageTemplateAction(label="圖書館", text="@圖書館營業時間/光復校區"),
                MessageTemplateAction(label="體育館", text="@體育館營業時間"),
                MessageTemplateAction(label="游泳館", text="@游泳館營業時間"),
                MessageTemplateAction(label="球館及球場", text="@球館及球場營業時間(光復校區)"),
            ],
        ),
    )
    return message


# 體育館營業時間
def stadium_hours():
    message = TextSendMessage(
        text="[體育館]"
        + "\n"
        + "週一至週五: 08:00~23:00"
        + "\n"
        + "-" * 20
        + "\n"
        + "[體育館重量訓練室]："
        + "\n"
        + "週一至週三: 17:00~22:00"
        + "\n"
        + "週四: 17:10~22:00"
        + "\n"
        + "(例假日、國定假日、寒暑假不開放)"
    )
    return message


# 游泳館營業時間(含健身中心)
def swimming_hours():
    message = TextSendMessage(
        text="[游泳館健身中心]"
        + "\n"
        + "週一至週五:"
        + "\n"
        + "07:00~12:00、13:00~22:00"
        + "\n"
        + "例假日、國定假日: 09:00~12:00、13:00~22:00"
        + "\n"
        + "-" * 20
        + "\n"
        + "[游泳館室內泳池]"
        + "\n"
        + "週一至週二: 公休"
        + "\n"
        + "週三至周五:"
        + "\n"
        + "14:00~16:00、16:30~18:30、19:00~21:30"
        + "\n"
        + "週六、週日:"
        + "\n"
        + "09:00~11:00、13:30~15:30、16:00~18:00"
        + "\n"
        + "-" * 20
        + "\n"
        + "[游泳館室外泳池]"
        + "\n"
        + "週一至週五: 07:00~09:30、16:00~18:30"
        + "\n"
        + "(開放時段依體育室公告)"
    )
    return message


# 球館及球場營業時間
def court_hours():
    message = TextSendMessage(
        text="[綜合球館]"
        + "\n"
        + "週一至週日: 08:00~23:00"
        + "\n"
        + "-" * 20
        + "\n"
        + "[羽球館]"
        + "\n"
        + "週一至週日: 08:00~23:00"
        + "\n"
        + "-" * 20
        + "\n"
        + "[室外球場]"
        + "\n"
        + "週一至週日: 06:00~23:00"
    )
    return message


def emergency_contact():
    message = ImagemapSendMessage(
        base_url='https://i.imgur.com/fIqhe2N.png',
        alt_text='緊急聯絡電話',
        base_size=BaseSize(width=1040, height=1040),
        actions=[
            URIImagemapAction(
                link_uri='tel:02-28261100',  # 陽明校區緊急電話
                area=ImagemapArea(
                    x=19, y=25, width=1000, height=499
                )
            ),
            URIImagemapAction(
                link_uri="tel:0972705757",  # 光復校區緊急電話
                area=ImagemapArea(x=27, y=522, width=982, height=493),
            ),
        ],
    )
    return message


# 校園資訊大圖
def campus_information():
    message = ImagemapSendMessage(
        base_url="https://i.imgur.com/42DceGK.png",
        alt_text="this is an imagemap",
        base_size=BaseSize(width=1040, height=1040),
        actions=[
            URIImagemapAction(
                link_uri="https://www.nycu.edu.tw/calendar/",
                area=ImagemapArea(x=0, y=0, width=346, height=346),
            ),
            MessageImagemapAction(
                text="@校園公告", area=ImagemapArea(x=346, y=0, width=346, height=346)
            ),
            MessageImagemapAction(
                text="@工讀資訊", area=ImagemapArea(x=692, y=0, width=348, height=346)
            ),
            MessageImagemapAction(
                text="@游泳館、體育館即時人數",
                area=ImagemapArea(x=0, y=346, width=346, height=346),
            ),
            MessageImagemapAction(
                text="@場館營業時間", area=ImagemapArea(x=346, y=346, width=346, height=346)
            ),
            MessageImagemapAction(
                text="@學餐資訊", area=ImagemapArea(x=692, y=346, width=348, height=346)
            ),
            MessageImagemapAction(
                text="@常見Q&A", area=ImagemapArea(x=0, y=692, width=346, height=348)
            ),
            MessageImagemapAction(
                text="@系所規定", area=ImagemapArea(x=346, y=692, width=346, height=348)
            ),
            MessageImagemapAction(
                text="@分享帳號", area=ImagemapArea(x=692, y=692, width=348, height=348)
            ),
        ],
    )

    return message


# 系所規定
def department_of_regulation():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="系所規定",
            text="請選取項目",
            actions=[
                MessageTemplateAction(label="系所申請", text="系所申請"),
                MessageTemplateAction(label="如何轉系", text="如何轉系"),
                MessageTemplateAction(label="畢業規定", text="畢業規定"),
            ],
        ),
    )
    return message


def button_SDGs():  # SDGs
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="SDGs",
            text="請選取項目",
            actions=[
                MessageTemplateAction(label="認識SDGs", text="@認識SDGs"),
                MessageTemplateAction(label="NYCU永續成果", text="@NYCU永續成果"),
                MessageTemplateAction(label="學院永續成果", text="@學院永續成果"),
                MessageTemplateAction(label="SDGs小遊戲", text="@SDGs小遊戲"),
            ],
        ),
    )
    return message


# 分機
def contact_first_layer():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="各處室位置分機",
            text="請選取單位",
            actions=[
                MessageTemplateAction(label="光復校區", text="@各處室位置分機(交通)"),
                MessageTemplateAction(label="陽明校區", text="@各處室位置分機(陽明)"),
            ],
        ),
    )
    return message


def jiau():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="各處室位置分機(交通)",
            text="請選取單位",
            actions=[
                MessageTemplateAction(label="行政單位", text="@行政單位(交通)"),
                MessageTemplateAction(label="教學單位", text="@教學單位(交通)"),
            ],
        ),
    )
    return message


def yawn():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="各處室位置分機(陽明)",
            text="請選取單位",
            actions=[
                MessageTemplateAction(label="行政單位", text="@行政單位(陽明)"),
                MessageTemplateAction(label="教學單位", text="@教學單位(陽明)"),
            ],
        ),
    )
    return message


def unit_button(unit_kind):  # 顯示單位
    if unit_kind == "行政單位":
        unit_table = administrative_unit
    elif unit_kind == "教學單位":
        unit_table = teaching_unit
    unit_c = []
    for unit in unit_table["單位"]:
        unit_c.append(
            CarouselColumn(
                title=unit,
                text="  ",
                actions=[MessageTemplateAction(label=unit, text="✦" + unit)],
            )
        )
    message = TemplateSendMessage(
        alt_text="NONE", template=CarouselTemplate(columns=unit_c)
    )
    return message


def y_unit_button(unit_kind):  # 顯示單位(陽明)
    if unit_kind == "行政單位(陽)":
        unit_table = y_administrative_unit
    elif unit_kind == "教學單位(陽)":
        unit_table = y_teaching_unit
    unit_c = []
    for unit in unit_table["單位"]:
        unit_c.append(
            CarouselColumn(
                title=unit,
                text="  ",
                actions=[MessageTemplateAction(label=unit, text="★" + unit)],
            )
        )
    message = TemplateSendMessage(
        alt_text="NONE", template=CarouselTemplate(columns=unit_c)
    )
    return message


def dep_button(unit, school):  # 顯示該單位部門
    dep_c = []
    print(school)
    if school == "交通":
        dep_table = pd.read_sql(
            "SELECT * FROM 學校各部門連絡方式 WHERE 單位='" + unit + "' AND 學校='交通'", cnxn
        )
        symbol = "✦"
    elif school == "陽明":
        dep_table = pd.read_sql(
            "SELECT * FROM 學校各部門連絡方式 WHERE 單位='" + unit + "' AND 學校='陽明'", cnxn
        )
        symbol = "★"

    for dep, ext, phone, place, web, opentime in zip(
        dep_table["部門"],
        dep_table["分機"],
        dep_table["專線"],
        dep_table["位置"],
        dep_table["網站"],
        dep_table["開放時間"],
    ):
        dep_c.append(
            CarouselColumn(
                title=dep,
                text="分機:" + ext + "\n專線:" + phone + "\n位置:" + place,
                # actions = [ URITemplateAction(label='網站',uri = web) ]
                actions=[
                    MessageTemplateAction(
                        label="詳細資訊與網站", text=symbol + dep + symbol)
                ],
            )
        )
    message = TemplateSendMessage(
        alt_text="NONE", template=CarouselTemplate(columns=dep_c)
    )
    return message


def dep_detail_info(dep):
    dep_info = pd.read_sql(
        "SELECT * FROM 學校各部門連絡方式 WHERE 部門='" + dep[1:] + "' ORDER BY 學校", cnxn
    )
    if dep_info.shape[0] > 1:
        if dep[0] == "✦":  # 交大
            dep_info = dep_info[dep_info["學校"] == "交通"]
        else:  # 陽明
            dep_info = dep_info[dep_info["學校"] == "陽明"]
            dep_info = dep_info.reset_index(drop=True)
    print(dep_info)

    message = [
        TextSendMessage(
            text=dep_info["部門"][0]
            + "\n分機:"
            + dep_info["分機"][0]
            + "\n專線:"
            + dep_info["專線"][0]
            + "\n位置:"
            + dep_info["位置"][0]
            + "\n開放時間:"
            + dep_info["開放時間"][0]
        ),
        LocationSendMessage(
            title="位置",
            address=dep_info["部門"][0],
            latitude=dep_info["緯度"][0],
            longitude=dep_info["經度"][0],
        ),
        TextSendMessage(text="網站:" + dep_info["網站"][0]),
    ]
    return message


def announcement():
    t, u = announce()
    message = TemplateSendMessage(
        alt_text="NONE",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[idx],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[idx])],
                )
                for idx in range(5)
            ]
            + [
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title="校園公告首頁",
                    text=" ",
                    actions=[
                        URITemplateAction(
                            label="前往首頁",
                            uri="https://infonews.nycu.edu.tw/index.php?SuperType=2&action=more&pagekey=1&categoryid=all",
                        )
                    ],
                )
            ]
        ),
    )
    return message


def announcement_covid19():
    t, u = announce_covid19()
    message = TemplateSendMessage(
        alt_text="NONE",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[0],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[0])],
                ),
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[1],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[1])],
                ),
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[2],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[2])],
                ),
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[3],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[3])],
                ),
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title=t[4],
                    text=" ",
                    actions=[URITemplateAction(label="詳細資訊", uri=u[4])],
                ),
                CarouselColumn(
                    # thumbnail_image_url = 'https://imgur.com/rgRhzDv.jpg',
                    title="防疫公告首頁",
                    text=" ",
                    actions=[
                        URITemplateAction(
                            label="前往首頁", uri="https://covid-news.nycu.edu.tw/"
                        )
                    ],
                ),
            ]
        ),
    )
    return message


def restaurant_button():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="餐廳營業時間",
            text="請選取校區",
            actions=[
                URITemplateAction(
                    label="光復校區學生餐廳",
                    uri="https://www.ga.nctu.edu.tw/general-division/rest/v-TmrI"
                    # uri = 'https://www.ga.nctu.edu.tw/web/page/attfile.php?u=TxYl9&t=pdf&n=110%E5%AD%B8%E5%B9%B4_%E5%AD%B8%E6%9C%9F%E9%96%93%E9%A4%90%E5%BB%B3%E7%87%9F%E6%A5%AD%E6%99%82%E9%96%93%E8%A1%A8-1100913.pdf'
                    # uri = 'https://www.ga.nctu.edu.tw/web/page/attfile.php?u=sYWl8&t=pdf&n=110%E5%B9%B4%E6%9A%91%E6%9C%9F%E9%A4%90%E5%BB%B3%E7%87%9F%E6%A5%AD%E6%99%82%E9%96%93%E*6%A8-1100728.pdf'
                ),
                URITemplateAction(
                    label="陽明校區學生餐廳", uri="https://gss.ym.edu.tw/files/90-1220-14.php"
                ),
            ],
        ),
    )
    return message


def gym_base():
    message = TemplateSendMessage(
        alt_text="NONE",
        template=ButtonsTemplate(
            title="游泳館、體育館即時人數",
            text="請選擇地點",
            actions=[
                MessageTemplateAction(label="游泳館健身房", text="@游泳館健身房人數"),
                MessageTemplateAction(label="游泳館游泳池", text="@游泳館游泳池人數"),
                MessageTemplateAction(label="體育館重訓室", text="@體育館重訓室人數"),
            ],
        ),
    )
    return message


# 所有的問題都沒有match到時，會來這邊做最後的搜尋
def interview_information(mtext):
    getAnswer = (
        "SELECT Answer from dbo.interview_information WHERE Question = '\n"
        + mtext
        + "';"
    )
    answers = pd.read_sql(getAnswer, cnxn)
    if answers.empty or answers["Answer"][0] == "":
        print("[" + mtext + "]:Can not find answer in interview_information")
        if mtext.find("/") > -1:
            mtext = mtext[: mtext.find("/")]
        getRepair = (
            "SELECT Repair from dbo.repair_table WHERE Intent = '\n" + mtext + "';"
        )
        repair = pd.read_sql(getRepair, cnxn)
        if repair.empty or repair["Repair"][0] == "":
            print("[" + mtext + "]:Can not find answer in repair_table")
            return [
                TextSendMessage(
                    text="小幫手無法辨識【"
                    + mtext
                    + "】這句話的意思，再麻煩您換句話說說看！\n\n或也可以透過【問題回饋】告知我們！謝謝您！"
                ),
                TemplateSendMessage(
                    alt_text="小幫手無法辨識【" + mtext + "】這句話的意思",
                    template=ButtonsTemplate(
                        title="問題回饋",
                        text="透過問題回饋告訴小幫手哪裏可以改進",
                        actions=[MessageTemplateAction(
                            label="問題回饋", text="@問題回饋")],
                    ),
                ),
            ]
        else:
            message = repair["Repair"][0]
    else:
        message = answers["Answer"][0]
    return TextSendMessage(message)


# 去handle user給予的回饋
def answer_feedback(mtext, user_id):
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    question = mtext.split("(|)")[1]
    feedback = mtext.split("(|)")[2]
    d = {
        "ID": [user_id],
        "Time": [now_time],
        "Question": [question],
        "Feedback": [feedback],
    }
    table = pd.DataFrame(data=d)
    # *** engine 修改 ***
    query = (
        "insert into 答案回饋 (ID,Time,Question,Feedback) values ('"
        + user_id
        + "','"
        + now_time
        + "','"
        + question
        + "','"
        + feedback
        + "')"
    )
    cnxn.cursor().execute(query)
    cnxn.cursor().commit()

    if feedback == "沒幫助":
        return TemplateSendMessage(
            alt_text="有意願的話再麻煩您透過【問題回饋】告知我們詳細問題",
            template=ButtonsTemplate(
                title="感謝您的回饋",
                text="有意願的話再麻煩您透過【問題回饋】告知我們詳細問題",
                actions=[MessageTemplateAction(label="問題回饋", text="@問題回饋")],
            ),
        )
    return TextSendMessage("感謝您的回饋！")


# 判斷是否是透過Button點選的資訊，以及對文字作前處理
def check_if_button_click(mtext):
    detail_Flag = False
    detail_request = " "

    if mtext == "結束":
        return mtext, detail_Flag, detail_request
    if ("@✦★#¥".find(mtext[0])) == -1:
        # 去掉文字的空白
        mtext_split = mtext.split(" ")
        mtext = ""
        for m in mtext_split:
            mtext += m
        mtext_split = mtext.split("\r\n")
        mtext = ""
        for m in mtext_split:
            mtext += m
        mtext_split = mtext.split("\n")
        mtext = ""
        for m in mtext_split:
            mtext += m
        response = CLU_analyze_intent( mtext )
        print(f"-----------\nrequest: {mtext}")
        print(f"response: {response}\n------------")
        getButtonmtext = (
            "SELECT Answer from dbo.mapping_intent WHERE Intent LIKE '%"
            + response
            + "%';"
        )
        buttonmtext = pd.read_sql(getButtonmtext, cnxn)
        # 不是問Button有的資訊
        if buttonmtext.empty:
            mtext = response
        else:
            mtext = buttonmtext["Answer"][0]

        if mtext.find("|") > -1:
            detail_Flag = True
            detail_request = mtext[mtext.find("|") + 1:]
            mtext = mtext[: mtext.find("|")]
    print(f"mtext: {mtext}")
    return mtext, detail_Flag, detail_request


# 進一步詢問系所、大樓資訊時
def ask_detail(mtext, user_id):
    comment = (
        "SELECT intent FROM dbo.ask_detail_table WHERE user_id LIKE '%"
        + user_id
        + "%'and bot_id = 1;"
    )
    intent = pd.read_sql(comment, cnxn)["intent"]

    if len(intent) != 0:
        # *** engine 修改 ***

        if mtext == "結束":
            query = (
                "delete from dbo.ask_detail_table where user_id like '%"
                + user_id
                + "%' and bot_id = 1"
            )
            cnxn.cursor().execute(query)
            cnxn.cursor().commit()
            return "@結束"
        elif mtext[0] == "@" or mtext[0] == "¥":
            query = (
                "delete from dbo.ask_detail_table where user_id like '%"
                + user_id
                + "%' and bot_id = 1"
            )
            cnxn.cursor().execute(query)
            cnxn.cursor().commit()
            return mtext

        if intent[0].split("/")[0] == "查詢教室、處室位置":
            mtext = "@" + intent[0] + "/" + mtext
        elif intent[0].split("/")[0] == "社團活動":
            mtext = "@" + intent[0] + "/" + mtext
        else:
            mtext = mtext + intent[0]

    return mtext


def campus_security_sop():
    return TemplateSendMessage(
        alt_text='校安SOP選單',
        template=ButtonsTemplate(
            title='校園安全SOP',
            text='請選取所需服務',
            actions=[
                MessageTemplateAction(
                    label='遺失事件處理要點',
                    text='@遺失事件處理要點'
                ), MessageTemplateAction(
                    label='車禍事件處理要點',
                    text='@車禍事件處理要點'
                ), MessageTemplateAction(
                    label='詐騙事件處理要點',
                    text='@詐騙事件處理要點'
                ), MessageTemplateAction(
                    label='性平事件處理要點',
                    text='@性平事件處理要點'
                )
            ]
        )
    )


if __name__ == "__main__":
    # app.run(port=8080)

    # 更改成hypercorn server
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config._bind = ["127.0.0.1:5000"]
    asyncio.run(serve(app, config))
