###########################################

# Poop Array V2.0

# This is a re-tweeter that responds to the hashtag #pooparray
# could interact directly w/ ParticleIO or maybe w/ AdafruitIO. 
# Depends, really. Will tinker around with both options. 

# Some Limitations:
# --> This only works if your account is public
# --> PYTHON 3: remember for print statements. 

# look up later
# http://stackoverflow.com/questions/9554087/setting-an-environment-variable-in-virtualenv
# https://realpython.com/blog/python/flask-by-example-part-1-project-setup/
# don't need this rn, but keep for later: http://stackoverflow.com/questions/2527892/parsing-a-tweet-to-extract-hashtags-into-an-array-in-python
# http://aadrake.com/using-twitter-as-a-stream-processing-source.html

############################################


# ===================== IMPORTS ========================== # 

import re, os, time, struct, requests, sys, json, random, threading

from random import choice
from threading import Thread

from twython import Twython, TwythonError
from twython import TwythonStreamer

from Adafruit_IO import Client

from requests.exceptions import ChunkedEncodingError
from queue import *			## dear SO I fucking hate your depths sometimes when it comes to finding answers about versioning. I TRULY DO. 


# ===================== I/O SETUP ========================== # 

ADAFRUIT_IO_KEY = os.environ['ADAFRUIT_IO_KEY']
aio = Client(ADAFRUIT_IO_KEY)

# ===================== VARIABLES ========================== # 

### crash redundancy. Basic. Pull the environment variable of the last saved count
### convert to int and assign it to tweet count, if you can't, make tweetCount zero
try:
	pullSaved = int(os.environ['SAVED_TWEET_COUNT'])
	tweetCount = pullSaved
except:
	tweetCount = 0

print("!tweetCount(saved): ",pullSaved)	
toFind = "#fuck2016"
# ===================== STREAMER ========================== # 

class TwitterStream(TwythonStreamer):
	def __init__(self, CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, tqueue):
		self.tweet_queue = tqueue
		super(TwitterStream, self).__init__(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

	def on_success(self, data):
		if 'text' in data:
			self.tweet_queue.put(data)

	def on_error(self, status_code, data):
		print(status_code)

# ===================== FUNCTIONS ========================== # 

def streamTweets(tweetsQu):
	""" Removing the stream from a blocking thing into a function...wowo I need to know more about this shit. """

	CONSUMER_KEY = os.environ['CONSUMER_KEY']
	CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
	OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
	OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

	## yes that's probably dirty, but fuck it. 
	global twitter

	twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twitter.verify_credentials()

	## pass to streamer
	try:
		stream = TwitterStream(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, tweetsQu)
		stream.statuses.filter(track=toFind) 
	except ChunkedEncodingError:
		streamTweets(tweet_queue)


def processTweets(tweetsQu):
	
	stopWords = set([
		'rape','raping','gangrape','gang rapes',
		'rapes','@','fortune','sale','gamergate',
		'follow','xxx','fb.me','tinyurl','gmail','hotmail','yahoo'
		])

	
	global tweetCount

	while True:
		data = tweetsQu.get()
		#body = data['text'].encode('utf-8')
		if 'text' in data:
			#print(data['text'].encode('utf-8'))
			## get your data as a string
			body = data['text']
			user = data['user']['screen_name']
			if not any(words in body for words in stopWords):
				if(toFind in body):
					#print(body)
					stripped = body.replace(toFind,'')
					toTweet = "{0} -{1}".format(stripped,user)
					print(toTweet)
					## might need a thing here in case i trip a spam 
					## if the body is over 140 charcters throw it out
					if(len(body) > 140):
						print("too long, discarded")
					else:
						twitter.update_status(status=toTweet)
						tweetCount+=1

		tweetsQu.task_done()
		

def streamUsage():
	""" Every Minute check how many tweets have been tweeted on the hashtag. Then send a command to Adafruit_IO indicating how busy the hashtag is."""
	starttime=time.time()
	global tweetCount
	tick = 0;
	while True:
		print("!streamUsage: tweetCount: {0}".format(tweetCount))
		## logic for tweet count
			## light, medium, heavy, insane
		if tweetCount >= 0 and tweetCount <= 3:
			aio.send('pooparray','10') 
			print("light usage: cmd-10")
		elif tweetCount > 3 and tweetCount <= 5:
			aio.send('pooparray','50') 
		elif tweetCount > 5 and tweetCount <= 10:
			aio.send('pooparray','100')
			print("medium usage: cmd-100")
		elif tweetCount > 10 and tweetCount <= 30:
			aio.send('pooparray','200')
			print("heavy usage: cmd-200")
		elif tweetCount > 30:
			aio.send('pooparray','300')
			print("INSANE: cmd-300")
		toSave = str(tweetCount)
		## every minute save the tweetCount as a string to the environment variable. 
		os.environ['SAVED_TWEET_COUNT'] = toSave
		
		## keep track of the minutes
		## reset everything every 5 hours, because why the fuck not right?
		## meh don't need a reset right now

		tick +=1
		print("tick: ",tick)
		"""
		if(tick == 300):
			tick = 0; ## five hours
			tweetCount = 0;
			os.environ['SAVED_TWEET_COUNT'] = "0"
		"""
		
		time.sleep(60.0 - ((time.time() - starttime) % 60.0)) ## every minute

# ===================== RUN THIS THING ========================== # 
		
try:
	### lookit all this god damn threading. One day I'm going to know more, and get better at this shit. 
	tweet_queue = Queue()
	t1 = Thread(target=streamTweets,args=(tweet_queue,))
	t2 = Thread(target=streamUsage)
	#t3 = Thread(target=resetCount)
	t1.setDaemon(True)
	t2.setDaemon(True)
	#t3.setDaemon(True)
	t1.start()
	t2.start()
	#t3.start()
	processTweets(tweet_queue)
	while True:
		pass
except KeyboardInterrupt:
	sys.exit(1)


# ===================== OLD SHIT ========================== # 

	
"""
def resetCount():
	## After 2 hours. Reset the count and start again. Remember Python does time in seconds. 
	global tweetCount
	print("!reset: tweetCount: {0}".format(tweetCount))
	print("time to reset the count")
	tweetCount = 0;
	print("!reset: tweetCount: {0}".format(tweetCount))

	
	starttime = time.time()
	while True:
		print("!reset: tweetCount: {0}".format(tweetCount))
		print("time to reset the count")
		tweetCount = 0;
		print("!reset: tweetCount: {0}".format(tweetCount))
		## also reset the environment variable
		#toSave = str(tweetCount)
		#os.environ['SAVED_TWEET_COUNT'] = toSave 
		time.sleep(7200.0 - ((time.time() - starttime) % 7200.0)) ## every 2 hours
"""
"""

# ===================== TWITTER SETUP ========================== # 

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

# ===================== VARIABLES ========================== # 

lookingFor = "#fuck2016"

## start a timer for every 15 minutes. look at the count

### no urls, no @tagging, no fb things, no emails
### I mean maybe I'll get rid of the images? But you never know.
stopWords = set([
	'rape','raping','gangrape','gang rapes',
	'rapes','@','fortune','sale','gamergate',
	'follow','xxx','fb.me','tinyurl','gmail','hotmail','yahoo'
	]) 

class poopStream(TwythonStreamer):

	def on_success(self, data):

		if 'text' in data:
			
			#print(data['text'].encode('utf-8'))
			## get your data as a string
			body = data['text']
			user = data['user']['screen_name']

			## might need to make ths better

			if not any(words in body for words in stopWords):
				if(lookingFor in body):
					print(body)
					stripped = body.replace(lookingFor,'')
					toTweet = "{0}: {1}".format(user,stripped)
					print(toTweet)
					#twitter.update_status(status=toTweet)
					aio.send('pooparray', 'tweet')
    

			
	def on_error(self, status_code, data):
		print(status_code)

		# Want to stop trying to get data because of the error?
		# Uncomment the next line!
		# self.disconnect()

# ===================== CALLBACKS ========================== # 

stream = poopStream(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
stream.statuses.filter(track='#fuck2016')
"""
#from Queue import Queue
#from multiprocessing import Queue