import json
import tweepy
from datamanager import DataManager
from player import Player

CONSUMER_KEY = "bBt8taxLy06yKaW0xUtvOjLWx"
CONSUMER_SECRET = "0YOFWR5Dekll6tUCuQXb5z5dNYid3OuMgaSKq7uPmgygplHIdY"
ACCESS_TOKEN = "695299748337549312-Unk9ugIUjtbRP5od17JtVjEOfAAZ8kx"
ACCESS_TOKEN_SECRET = "ZczjHMlCK86kp1BORluORsd3oxuGAqwhFPTzrX0hKkgEC"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
filter_track = '@450bot'
game_id = 0
host_player = ""
player_list = []

class TweetListener(tweepy.StreamListener):
	def on_data(self, data):
		# Twitter returns data in JSON format - we need to decode it first
		decoded = json.loads(data)
		
		# Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
		user = decoded['user']
		text = decoded['text'].encode('ascii', 'ignore')
		
		# Strip the "@450bot " beginning of the tweet
		text = text[len(filter_track) + 1:]
		if text == "join":
			player = Player(user)
			if len(player_list) == 0:
				self.new_game()
				host_player = player
			player_list.append(player)
			print(player.get_screen_name(), "has joined the game.")
		
		return True
    
	def on_error(self, status):
		print status
		
	def new_game(self):
		# Tweet the game id to get around the duplicate status error.
		game_id = DataManager.get_last_game_id()
		game_id += 1
		DataManager.save_game_id(game_id)
		api.update_status("(Game #" + str(game_id) + ") A new game has been created. Tweet '@450bot join' to join the game.")
	
def main():
	l = TweetListener()
	stream = tweepy.Stream(auth=api.auth, listener=l)
	stream.filter(track=[filter_track])
		
if __name__=="__main__":
	main()
	