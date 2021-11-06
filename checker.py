#!/usr/bin/python3
# -*- coding: utf-8 -*-
import tweepy
import re
import sqlite3
from datetime import datetime as dt
import os
import sys
import re
from dotenv import load_dotenv
load_dotenv()

dbname = 'tweets.db'

target_id = os.getenv('TARGET_ID')
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token_key = os.getenv('ACCESS_TOKEN_KEY')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

def getProtectInfo(user_id):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit = True)
	user_status = api.get_user(user_id)
	return user_status.protected

def getTweetInfo(id):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit = True)
	tweet_status = api.statuses_lookup([id], tweet_mode='extended')
	if len(tweet_status) > 0:
		return tweet_status[0]
	else:
		return None
		
def notify(content):
	# ここの部分は任意に変えてください
	# 例)ツイッターでつぶやく、LINEやSlackで自分に通知するなど

	#auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	#auth.set_access_token(access_token_key, access_token_secret)
	#api = tweepy.API(auth, wait_on_rate_limit = True)
	
	#api.update_status(content)
	print(content)

if __name__ == "__main__":
	# 鍵垢だったら即終了する
	if getProtectInfo(target_id):
		sys.exit()

	conn = sqlite3.connect(dbname)
	c = conn.cursor()

	# 削除済みのツイート一覧を取得する
	sql = "SELECT tweet_id,content,image1,image2,image3,image4,created_at FROM deleted ORDER BY tweet_id DESC"
	res = c.execute(sql)
	deleted = {}
	addlist = []

	for r in res:
		deleted[r[0]] = 1

	# 過去に取得したツイートを取得する
	sql = "SELECT tweet_id,content,image1,image2,image3,image4,created_at FROM tweet ORDER BY tweet_id DESC"
	res = c.execute(sql)

	cnt = 0
	for r in res:
		# そのツイートは存在するか？
		exist = getTweetInfo(r[0])

		if not exist:
			if not r[0] in deleted:
				# 削除済みツイートとして登録する
				sql = 'INSERT INTO deleted VALUES(\"' + r[0] + '\", \"' + r[1]+ '\",' 
				for i in range(2,6):
					if r[i]:
						sql += "\"" + r[i] + "\","
					else:
						sql += "null,"
				sql += ' \"' + r[6] +  '\")'
				addlist.append(sql)

				# ツイ消し通知のメッセージを作る
				text = target_id + "がツイ消ししました\n\n"
				content = r[1]
				content = content[0:110]
				text += "[" + r[6] + "]\n" # 日付
				text += content

				# RTは除外する
				if not re.match("RT ", r[1]):
					notify(text)
		cnt += 1
		# データベースが増えすぎた時のために上限をもうけておく
		if cnt > 2000:
			break

	# データベースを更新する
	for sql in addlist:
		c.execute(sql)

	conn.commit()
	conn.close()
