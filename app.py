from __future__ import print_function

import time
import threading as td
from datetime import datetime
from pytz import timezone

# import gspread
import re
import os

# from apiclient.discovery import build
# from httplib2 import Http
# from oauth2client import file, client, tools

from flask import Flask, request, abort
from urllib.request import urlopen
# from oauth2client.service_account import ServiceAccountCredentials

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('n19IlRMRXK05Vf7+Kunl0Y7NxrcStBVcTOy3whJzNVoQbNLTHnfk7Ww3ciGKVJdEg/ioT4zXlVGauWR5l4SOdxxpH2gH/oJ9pVS2aZ4R0Hnm1QKv3T2qDiRfec0XRF31Xjdu1z7oB4gwm/rrHxY/TQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('9ffa9b07f9a2dfef20cffd300af6df4e')

# global variables
app_name = '髮落士報時'
version = 68
mode = 1
has_said = 0
fmt = '%H:%M'
systime = timezone('Asia/Taipei')
sysregion = 'TW'
usage_cmd = '[可用指令] \ntest\t- BOT版本 \ntime\t- 報時 \n/stop\t- 關閉BOT \n/start\t- 開啟BOT \n/help\t- 可用指令'
# ----------------------------------------------------------
class myThread (td.Thread):
   def __init__(self, user_message, event):
      td.Thread.__init__(self)
      self.user_message = user_message
      self.event = event

   def run(self):
      onPlayerTalk(self.user_message, self.event)    

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global app_name, version, mode
    user_message = event.message.text.lower()
    # console command
    if(user_message == "test"):
        message = TextSendMessage(text='歡迎使用'+app_name+' v1.'+str(version)+'！')
        line_bot_api.reply_message(event.reply_token,message)
    elif(user_message == "/stop"):
        message = TextSendMessage(text=app_name+'已被關閉！')
        line_bot_api.reply_message(event.reply_token,message)
        mode = 0
    elif(user_message == "/start"):
        message = TextSendMessage(text=app_name+'已經開啟！')
        line_bot_api.reply_message(event.reply_token,message)
        mode = 1    
    elif(user_message == "/help"):
        usage(event)
    # other command using thread
    else:
        myThread(user_message, event).start()

def usage(event):
    global usage_cmd
    message = TextSendMessage(text=usage_cmd)
    line_bot_api.reply_message(event.reply_token,message)
    
def hour_Convert(Hour):
    if(Hour >= 0 and Hour <= 3):
        return "凌晨 " + str(Hour)
    elif(Hour >= 4 and Hour <= 6):
        return "清晨 " + str(Hour)
    elif(Hour >= 7 and Hour <= 11):
        return "早上 " + str(Hour)
    elif(Hour == 12):
        return "中午 " + str(Hour)
    elif(Hour >= 13 and Hour <= 18):
        return "下午 " + str(Hour - 12)
    elif(Hour >= 19 and Hour <= 23):
        return "晚上 " + str(Hour - 12)

def set_timeRegion_TW():
    global systime, sysregion
    systime = timezone('Asia/Taipei')
    sysregion = 'TW'
    return "台北"

def set_timeRegion_JP():
    global systime, sysregion
    systime = timezone('Asia/Tokyo')
    sysregion = 'JP'
    return "東京"

def set_timeRegion_AUQLD():
    global systime, sysregion
    systime = timezone('Australia/Brisbane')
    sysregion = 'AU/QLD'
    return "布里斯本"

def set_timeRegion_AUMEL():
    global systime, sysregion
    systime = timezone('Australia/Melbourne')
    sysregion = 'AU/MEL'
    return "墨爾本"

def switchRegion(argu):
    if(argu == "tw"):
        return set_timeRegion_TW()
    elif(argu == "jp"):
        return set_timeRegion_JP()
    elif(argu == "qld"):
        return set_timeRegion_AUQLD()
    elif(argu == "mel"):
        return set_timeRegion_AUMEL()
    else:
        return "Invalid"

# english characters have been lower cased. Refer handle_message(event):
def    onPlayerTalk(user_message, event):
    global mode, has_said, systime, sysregion, fmt
    time = str(datetime.now(systime).strftime(fmt))
    (Hr, Mn) = time.split(':')
    # Sc = str(datetime.time.second)
    # only process message when mode = 1;
    if(mode == 1):
        if(user_message == "報時" or user_message == "time"):
            reply_message = "真棒 " + hour_Convert(int(Hr)) + " 時 " + Mn + " 分("+sysregion+")了！！"
            message = TextSendMessage(text = reply_message)
            line_bot_api.reply_message(event.reply_token, message)

        elif(user_message.find("timezone ") == 0):
            argu = user_message.lstrip("timezone ")
            result = switchRegion(argu)
            reply_message = "NULL" #declare
            if(result == "Invalid"):
                reply_message = ("使用：timezone [tw/jp/qld/mel]")
            else:
                reply_message = ("棒棒 系統時間已被設定為 " + result + " 時區.")
            message = TextSendMessage(text = reply_message)
            line_bot_api.reply_message(event.reply_token, message)
            
        if(int(Mn) == 0 and has_said == 0):
            has_said = 1
            reply_message = "好棒 " + hour_Convert(int(Hr)) + " 點("+sysregion+")了!"
            # reply_message = "好棒 " + hour_Convert(int(Hr)) + " 點了～"
            message = TextSendMessage(text = reply_message)
            line_bot_api.reply_message(event.reply_token, message)
    
    # reset said @ minute = 30 prevent spam
    if(int(Mn) >= 3 and has_said == 1):
        has_said = 0
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
