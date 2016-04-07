#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API
from tweepy import Stream
import json
import logging
import warnings
from pprint import pprint

import sys
import time

import atexit

f = ''
twitts = []

def exitfunc():
	global twitts
	savetwitts(twitts)

def loadtwitts(twitts):
	f = open('twitts.txt', 'r')
	x = f.readlines()
	for line in x:
		twitts.append(line.replace('\n','').replace('\r',''))
	f.close()

def savetwitts(twitts):
	f = open('twitts.txt', 'w')
	f.writelines("%s\n" % l for l in twitts)
	f.close()
 
AVOID = ["monty", "leather", "skin", "bag", "blood", "bite"]

track=['bitcoin giveway','paypal giveaway','giveaway', 'contest', 'concurso', 'sorteo']

class PyStreamListener(StreamListener):
    def __init__(self):
	self.allow_follow=True

    def on_data(self, data):
        tweet = json.loads(data)
        try:

		#print tweet
		
		if tweet['id'] not in twitts:	
            		publish = True
            		for word in AVOID:
                		if word in tweet['text'].lower():
                    			logging.info("SKIPPED: {}".format(word))
                    			publish = False
 
            		if tweet.get('lang') and tweet.get('lang') != 'en':
                		publish = False
 
            		if publish:
				time.sleep(5)
                		twitter_client.retweet(tweet['id'])
                		msg = "RT: {}".format(tweet['text'].encode('utf-8'))
				logging.debug(msg)
 				print  msg
				user_id = tweet['user']['id']
				
				if self.allow_follow == True:
					twitter_client.create_friendship(user_id,'follow')
					print "followed: ", user_id
			
				twitts.append(tweet['id'])

		else:
			print 'cache hit: ', tweet['id']
			
        except Exception as ex:
		print 'ex:',ex
		if ex[0][0]['code'] == 185:
			sys.exit()

		if ex[0][0]['code'] == 161:
			self.allow_follow = False
			print 'allow_follow:',self.allow_follow

		if ex[0][0]['code'] == 327:
			print tweet['id']
                        twitts.append(tweet['id'])
	

	return True
 
    def on_error(self, status):
        print 'status:',status
 
if __name__ == '__main__':


	print "Starging Bot..."
	logging.getLogger("main").setLevel(logging.DEBUG)
	logging.debug('Twittbot starting...')
	print "loading twitts..."	
	loadtwitts(twitts)

	atexit.register(exitfunc)
	

	warnings.filterwarnings("ignore")
 
	access_token = ""
	access_token_secret = ""
	consumer_key = ""
	consumer_secret = ""
 
	auth_handler = OAuthHandler(consumer_key, consumer_secret)
	auth_handler.set_access_token(access_token, access_token_secret)
 
	twitter_client = API(auth_handler,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,compression=True)
 
	listener = PyStreamListener()
    	stream = Stream(auth_handler, listener)
    	stream.filter(track=track)

