#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import geopy.distance as ps

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = 'tAVxtDE0Imrv91ENrACuDwf4/iGoRu1dlpMRNCWRVRyQKgLLdV54LdGI0CMjWU2LwHGqbSLAdI/L1J/7VwRdh/NENbLBjycnN+JgwF7Y4kdLkqu40tTm6uLgXR4klP2E4mBK6QR9koApsOGwYLMjrwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

casedata = pd.read_excel('casedata.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200

def getdistace(latitude, longitude,cdat):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = cdat[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(ps.vincenty(coords_1, coords_2).km)
  return kmsumList

def handle_location(lat,lng,cdat,topK):
    result = getdistace(lat, lng,cdat)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.1f'%(result.iloc[i]['km'])
        newssource = str(result.iloc[i]['News_Soruce'])
        txtResult = txtResult + kmdistance + '\n' + newssource + '\n\n'
    return txtResult[0:-2]

def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        txtresult = handle_location(lat,lng,casedata,3)
        replyObj = TextSendMessage(text=msg)
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

if __name__ == '__main__':
    app.run(debug=True)
