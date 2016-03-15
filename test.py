import tweepy
import time
# import exceptions
from urllib2 import HTTPError

CONSUMER_KEY = "bBt8taxLy06yKaW0xUtvOjLWx"
CONSUMER_SECRET = "0YOFWR5Dekll6tUCuQXb5z5dNYid3OuMgaSKq7uPmgygplHIdY"
ACCESS_TOKEN = "695299748337549312-Unk9ugIUjtbRP5od17JtVjEOfAAZ8kx"
ACCESS_TOKEN_SECRET = "ZczjHMlCK86kp1BORluORsd3oxuGAqwhFPTzrX0hKkgEC"

def save_id(statefile,id):
    """Save last status ID to a file"""
    last_id = get_last_id(statefile)

    if last_id < id:
        print('Saving new ID %d to %s' % (id,statefile))
        f = open(statefile,'w')
        f.write(str(id)) # no trailing newline
        f.close()
    else:
        print('Received smaller ID, not saving. Old: %d, New: %s' % (
            last_id, id))

def get_last_id(statefile):
    """Retrieve last status ID from a file"""

    print('Getting last ID from %s' % (statefile,))
    try:
        f = open(statefile,'r')
        id = int(f.read())
        f.close()
    except IOError:
        print('IOError raised, returning zero (0)')
        return 0
    print('Got %d' % (id,))
    return id
	
def careful_retweet(api, tweet):
	#normalized_tweet = tweet.text.lower().strip()
	
	print("new tweet: %s" % (tweet.text))
	return
	
def main():
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	
	lastidfile = "lastid.txt"
	while 1:
		last_id = get_last_id(lastidfile)
		public_tweets = api.home_timeline()
		for tweet in public_tweets:
			if tweet.id > last_id:
				try:
					careful_retweet(api,tweet)
				except HTTPError, e:
					print e.code()
					print e.read()
				except Exception, e:
					print 'e: %s' % e
					print repr(e)
				else:
					save_id(lastidfile, tweet.id)
		time.sleep(60)
		
if __name__=="__main__":
	main()
	
"""
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text
"""