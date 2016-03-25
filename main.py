import json
import tweepy
import gamecontroller as gc
from datamanager import DataManager
from player import Player

CONSUMER_KEY = "bBt8taxLy06yKaW0xUtvOjLWx"
CONSUMER_SECRET = "0YOFWR5Dekll6tUCuQXb5z5dNYid3OuMgaSKq7uPmgygplHIdY"
ACCESS_TOKEN = "695299748337549312-tX6v3y0Yk9TuS6Hjf7FEs5eudhdtHp3"
ACCESS_TOKEN_SECRET = "z6avibQB5JwFVPa4xyTr0lUs56XkxwmzVgS43CS3b3e2L"
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

	"""
	def on_data(self, data):
		global host_player
		global game
		
		# Twitter returns data in JSON format - we need to decode it first
		decoded = json.loads(data)
		print(decoded)
		
		# Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
		user = decoded['user']
		text = decoded['text'].encode('ascii', 'ignore')
		player = None
		#try to find the player in the player_list
		if gc.user_exists(user, player_list):
			player = gc.get_player(user, player_list)
		else:
			player = Player(user)
		
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
				game_id = DataManager.get_last_game_id()
				api.update_status( "(Game #" + str(game_id) + ") @" + player.screen_name + " you started the game, make your first move!")
			else:
				api.update_status("@" + player.screen_name + "you are not allowed to start this game")
		elif text == "shoot" or text == "reload" or text =="defend" or text == "Bang":
			game.get_reply(player,text)
				
 
		return True
   """
	
	def on_direct_message(self, status):
		"""Called when a direct message is received.
		
		Direct message json keys:
			created_at
			recipient_id_str
			sender
			sender_id_str
			text
			sender_screen_name
			sender_id
			entities
			recipient_id
			id_str
			recipient_screen_name
			recipient
			id
		"""
		dm = status._json['direct_message']
		sender = dm['sender']
		print(sender['screen_name'])
		print(dm['text'])
	
	def on_error(self, status):
		print status
		
		
	def join_game(self, player):
		if player in player_list:
			print(player.screen_name + " has already joined the game.")
		else:
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
	global player_list
	def __init__(self):
		self.player_num = len(player_list)
		self.count_reply = 0
		self.gameover_list =[]
	def get_reply(self,who,reply):
		print(who)
		print(player_list.index(who))
		self.count_reply+=1
		#check if the player replied
		player_list[player_list.index(who)].reply = 1
		#0:reload, 1:shoot,2:defend,3:bang
		
		
		if reply == "shoot":
			if player_list[player_list.index(who)].qi == 0:
				#send direct msg here. by default set to reload.
				player_list[player_list.index(who)].move = 0
			else:
				player_list[player_list.index(who)].move = 1
		elif reply == "reload":
			player_list[player_list.index(who)].move = 0
			player_list[player_list.index(who)].qi += 1
		elif reply == "defend":
			player_list[player_list.index(who)].move = 2
		elif reply == "Bang":
			player_list[player_list.index(who)].move = 3
		
		if self.count_reply == self.player_num:
			result = self.get_result()
		
		
	def get_result(self):
		#the attack 
		for player in player_list:
			#Bang attack. Undefendable
			if player.move == 3:
				for player2 in player_list:
					if player2.move != 3:
						self.gameover_list.append(player)
				sn = player.screen_name
				m = "@%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.update_status(m,player.id)
			#normal attack, defendable

			elif player.move == 1:
				for player2 in player_list:
					if player2.move == 0:
						self.gameover_list.append(player)
				sn = player.screen_name
				m = "@%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.update_status(m,player.id)
		#nobody attack, then everyone is safe
		if self.gameover_list ==[]:
			m = "looks like everyone is safe this round! What about your next move?"
			api.update_status(m)
		#send msg to the dead men	
		for player in self.gameover_list:
			sn = player.screen_name
			m = "@%s I'm sorry,you've eliminated in this round..."%(sn)
			api.update_status(m,player.id)
			player_list.remove(player)
		#reset the moves to reload
		for player in player_list:
			player.move = 0
		
		
		self.gameover_list = []
		self.count_reply = 0
		self.player_num = len(player_list)
		
		#end the game
		if len(player_list) == 1:
			player = player_list[0]
			sn = player.screen_name
			m = "@%s Nicely done! You are the winner of this round!"%(sn)
			api.update_status(m,player.id)
			
	
	
def main():
	l = TweetListener()
	stream = tweepy.Stream(auth=api.auth, listener=l)
	#stream.filter(track=[filter_track])
	stream.userstream()
		
if __name__=="__main__":
	main()
	