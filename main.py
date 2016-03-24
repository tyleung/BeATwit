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
game = None

class TweetListener(tweepy.StreamListener):
	join_str = "join game " + str(game_id)
	
	def on_data(self, data):
		global host_player
		global game
		# Twitter returns data in JSON format - we need to decode it first
		decoded = json.loads(data)
		
		# Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
		user = decoded['user']
		text = decoded['text'].encode('ascii', 'ignore')
		player = Player(user)
		screenname = decoded['user']['screen_name']
		
		# Strip the "@450bot " beginning of the tweet
		text = text[len(filter_track) + 1:]
		if text == "create" and len(player_list) == 0:
			self.new_game()
			self.join_game(player)
			host_player = player.screen_name
			print(player.screen_name)
		elif text == join_str:
			self.join_game(player)
		elif text == "start":
			if player.screen_name == host_player:
				game = playGame()
				api.update_status( "(Game #" + str(game_id) + ") @" + screenname + "you started the game, make your first move!")
			else:
				api.update_status("@" + screenname + "you are not allowed to start this game")
		elif text == "shoot" or text == "reload" or text =="defend" or text == "Bang":
			game.get_reply(user,text)
				
		return True
    
	def on_error(self, status):
		print status
		
		
	def join_game(self, player):
		#player = Player(user)
		for p in player_list:
			if p.screen_name == player.screen_name:
				print(player.screen_name + " has already joined the game.")
				return
		player_list.append(player)
		print(player.screen_name + " has joined the game.")
	
	def new_game(self):
		# Tweet the game id to get around the duplicate status error.
		game_id = DataManager.get_last_game_id()
		game_id += 1
		DataManager.save_game_id(game_id)
		global join_str
		join_str = "join game " + str(game_id)
		api.update_status("(Game #" + str(game_id) + ") A new game has been created. Tweet '@450bot " + join_str + "' to join the game.")
		
		
		
class playGame:
	
	count_reply = 0
	gameover_list =[]
	player_num = 0
	def __init__(self):
		player_num = len(player_list)
		
	def get_reply(self,who,reply):
		self.count_reply+=1
		#check if the player replied
		player_list[index(who)].reply = 1
		#0:reload, 1:shoot,2:defend,3:bang
		
		
		if reply == "shoot":
			player_list[index(who)].move = 1
		elif reply == "reload":
			player_list[index(who)].move = 0
			player_list[index(who)].qi += 1
		elif reply == "defend":
			player_list[index(who)].move = 2
		elif reply == "Bang":
			player_list[index(who)].move = 3
		
		if count_reply == player_num:
			result = get_result()
		
		
	def get_result(self):
		for player in player_list:
			if player.move == 3:
				for player2 in player_list:
					if player2.move != 3:
						gameover_list.append(player)
				sn = player.screen_name
				m = "@%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.update_status(m,player.id)

			elif player.move == 1:
				for player2 in player_list:
					if player2.move == 0:
						gameover_list.append(player)
				sn = player.screen_name
				m = "@%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.update_status(m,player.id)
			
		for player in gameover_list:
			sn = player.screen_name
			m = "@%s I'm sorry,you've eliminated in this round..."%(sn)
			api.update_status(m,player.id)
			player_list.remove(player)
		
		for player in player_list:
			player.move = 0
		
		
		gameover_list = []
		count_reply = 0
		
		if len(player_list) == 1:
			player = player_list[0]
			sn = player.screen_name
			m = "@%s Nicely done! You are the winner of this round!"%(sn)
			api.update_status(m,player.id)
			
	
	
def main():
	l = TweetListener()
	stream = tweepy.Stream(auth=api.auth, listener=l)
	stream.filter(track=[filter_track])
		
if __name__=="__main__":
	main()
	