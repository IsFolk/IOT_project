from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import configparser

import json
import run
import threading
from pyngrok import ngrok

import globals


app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


userId = ""
# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    bodyjson = json.loads(request.get_data(as_text=True))
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        userId = bodyjson["events"][0]["source"]["userId"]
        #print(userId)
        #print(bodyjson["events"][0]["message"]["text"])
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    userId = event.source.user_id
    print(userId)
    #print("nothing")
    now_message = event.message.text
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        timestart = now_message.index("設置時間")+5
        #print("timestart:"+str(timestart))
        tmpstr = ""
        timeloop = 0
        
        time_list = []
        for i in range(len(now_message)-timestart):
            timeloop += 1            
            #print("timeloop"+str(timeloop))
            if timeloop % 9 == 0 and timeloop != 0:
                timeloop = 0
                timestart += 1
                continue
            tmpstr += now_message[timestart]
            #print(tmpstr)
            if timeloop % 8 == 0 and timeloop != 0:
                time_list.append(tmpstr)
                tmpstr = ""
                #print(tmpstr)
            timestart += 1

        #print(event.message.text)

        loop = 0
        if("開始監控" in event.message.text):
            #print(time_list)
            resp = "開始監控 ,設置時間為:"
            for each in time_list:
                each += " "
                resp += each
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=resp)
                )

            
            #ssh_tunnel = ngrok.connect(8000, "tcp")
            
            print(userId)
            while True:           
                outcome = run.run(time_list)
                #print(outcome)
                if(outcome is not None):
                    line_bot_api.push_message(userId, 
                          TextSendMessage(text=outcome[0]))
                    
                    line_bot_api.push_message(userId, 
                          {
                              "type": "video",
                              "originalContentUrl":"https://www.youtube.com/watch?v=" + globals.youtubeid,
                              "previewImageUrl": "https://imgur.com/a/lktXXFZ"
                          })
                    
                    
                 
                 
    
if __name__ == "__main__":
    globals.initialize("")
    app.run()