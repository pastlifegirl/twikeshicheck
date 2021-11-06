#!/usr/bin/python3
# -*- coding: utf-8 -*-
import tweepy
import re
import sqlite3
from datetime import datetime as dt
import os
from dotenv import load_dotenv
load_dotenv()

dbname = 'tweets.db'

target_id = os.getenv('TARGET_ID')
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token_key = os.getenv('ACCESS_TOKEN_KEY')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)

conn = sqlite3.connect(dbname)
c = conn.cursor()

# 呼び出されると最新のツイートをひろってくる
if __name__ == "__main__":
	for status in api.user_timeline(screen_name=target_id, count = 1000):
		img = 0
		sql_img = ""

		# 画像がある場合は画像もDLしておく
		if hasattr(status, 'extended_entities'):
			entity = status.extended_entities['media']
			for media in entity:
				sql_img += ",\"" + str(status.id) + "_" + str(img) +".jpg\""
				# 重複する画像は保存しない
				if not os.path.exists("./image/" + str(status.id) + "_" + str(img) +".jpg"):
					os.system("wget -O ./image/" + str(status.id) + "_" + str(img) +".jpg " + media['media_url'])
				img += 1
		for n in range(4-img):
			sql_img += ",null"

		sql = 'INSERT INTO tweet VALUES(\"' + str(status.id) + '\", \"' + status.text + '\"' + sql_img +  ', \"' + str(status.created_at) +  '\")'
		c.execute(sql)

	conn.commit()
	conn.close()
