#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author Dario Clavijo

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

access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""

f = ''
twitts = []
follows = []

def exitfunc():
	global twitts
	global follows
	print "saving state..."
	savefile('follows.txt',follows)
	savefile('twitts.txt',twitts)

def loadfile(filename,var):
	f = open(filename, 'r')
        x = f.readlines()
        for line in x:
                var.append(line.replace('\n','').replace('\r',''))
        f.close()

def savefile(filename,var):
	f = open(filename, 'w')
	f.writelines("%s\n" % l for l in var)
	f.close()
 
AVOID = ["monty", "leather", "skin", "bag", "blood", "bite"]

track=['bitcoin giveway','paypal giveaway','giveaway', 'contest', 'concurso', 'sorteo']


class PyStreamListener(StreamListener):
    def __init__(self):
	self.allow_follow=True
	self.paused = False	
	self.i = 0.5

    def on_data(self, data):
	tweet = json.loads(data)
        try:
		if not self.paused:
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
                			msg = "{}".format(tweet['text'].encode('utf-8'))
					logging.debug(msg)
 					print  msg
					user_id = tweet['user']['id']
				

					if self.allow_follow == True:
						if user_id not in follows:
							twitter_client.create_friendship(user_id,'follow')
							print "FW: ", user_id
							follows.append(user_id)
						else:
							print "already followed: ", user_id
			
					twitts.append(tweet['id'])

			else:
				print 'cache hit: ', tweet['id']
			
        except Exception as ex:
		print 'ex:',ex
		if ex[0][0]['code'] == 185:
			self.paused = True
			self.i = self.i * 2
			j = self.i*15*60
			print "paused for %i..." % j
			time.sleep(j)
			self.paused = False
			#self.i = 1
			self.allow_follow = True

		if ex[0][0]['code'] == 161:
			self.allow_follow = False
			print 'allow_follow:',self.allow_follow

		if ex[0][0]['code'] == 327:
			print tweet['id']
                        twitts.append(tweet['id'])
	

	return True

    def on_limit(self,track):
	print "on limit:",track
 
    def on_error(self, status):
        print 'status:',status
 
if __name__ == '__main__':


	print "starging bot..."
	logging.getLogger("main").setLevel(logging.DEBUG)
	logging.debug('Twittbot starting...')
	print "loading twitts..."	
	
	loadfile('follows.txt',follows)
	loadfile('twitts.txt',twitts)

	atexit.register(exitfunc)
	
	warnings.filterwarnings("ignore")
 
	auth_handler = OAuthHandler(consumer_key, consumer_secret)
	auth_handler.set_access_token(access_token, access_token_secret)
 
	twitter_client = API(auth_handler,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,compression=True)
 
	listener = PyStreamListener()
    	stream = Stream(auth_handler, listener)
    	
	try:
    		stream.filter(track=track)
	except:
		print "execution error..."
		exitfunc()
	#	#sys.exit()

