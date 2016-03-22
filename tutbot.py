import tweepy
import time
# import exceptions
from DataManager import DataManager
from urllib2 import HTTPError
#from nltk.chat import eliza
#CONSUMER_KEY = "z0ou9dxlx7NEEBnkCynoeslWJ"
#CONSUMER_SECRET = "Mol8e3xa5V8zZwHkaoXkPmFtDN1SvF4KsGruMLke0Wisy1RedH"
#ACCESS_TOKEN = "4826311692-6mcxZiquAseGU9PCA3X4XqQQugKx4VTfiY0ZMby"
#ACCESS_TOKEN_SECRET = "oDdvmAi6G7ZtqBpTZWaFHf1FiCcCbSB17IxNGHmYdDIR0"
CONSUMER_KEY = "bBt8taxLy06yKaW0xUtvOjLWx"
CONSUMER_SECRET = "0YOFWR5Dekll6tUCuQXb5z5dNYid3OuMgaSKq7uPmgygplHIdY"
ACCESS_TOKEN = "695299748337549312-Unk9ugIUjtbRP5od17JtVjEOfAAZ8kx"
ACCESS_TOKEN_SECRET = "ZczjHMlCK86kp1BORluORsd3oxuGAqwhFPTzrX0hKkgEC"

#chatbot = eliza.Chat(eliza.pairs)

class ReplyToTweet(tweepy.StreamListener):
	def on_data(self, data):
		# Twitter returns data in JSON format - we need to decode it first
		decoded = json.loads(data)
		# Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
		print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
		print ''

		sn = decoded['user']['screen_name']
		m = "@%s Hello!" %(sn)
		s = api.update_status(m,decoded['id'])
		
		return True
    
	def on_error(self, status):
		print status    

if __name__ == '__main__':
	l = ReplyToTweet()
	auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
	auth.secure = True
	api = tweepy.API(auth)    

	stream = tweepy.Stream(auth,l)
	#stream.filter(track=['#TwitGame'])
	stream.filter(track=['@450bot'])