import json
import tweepy
from datamanager import DataManager
from gamecontroller import GameController as gc
from player import Player

CONSUMER_KEY = "bBt8taxLy06yKaW0xUtvOjLWx"
CONSUMER_SECRET = "0YOFWR5Dekll6tUCuQXb5z5dNYid3OuMgaSKq7uPmgygplHIdY"
ACCESS_TOKEN = "695299748337549312-tX6v3y0Yk9TuS6Hjf7FEs5eudhdtHp3"
ACCESS_TOKEN_SECRET = "z6avibQB5JwFVPa4xyTr0lUs56XkxwmzVgS43CS3b3e2L"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

game_id = 0
host_player = Player()
move_list = {"shoot": 0, "reload": 1, "defend": 2, "bang": 3}
player_list = []
game = None

class TweetListener(tweepy.StreamListener):
	
	def __init__(self):
		super(TweetListener, self).__init__()
		self.game_created = False
		
	#def on_data(self, data):
	#	return True
	
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
		global host_player
		dm = status._json['direct_message']
		sender = dm['sender']
		text = dm['text'].encode('ascii', 'ignore').lower()
		
		player = None
		if gc.user_exists(sender, player_list):
			player = gc.get_player(sender, player_list)
		else:
			player = Player(sender)
		
		if not self.game_created:
			if text == "create" and len(player_list) == 0:
				self.new_game()
				self.join_game(player)
				host_player = player
				api.send_direct_message(user=player.id, text="You are the host player. Send 'start' to start the game when everyone has joined.")
				self.game_created = True
		else:
			if text == "join":
				self.join_game(player)
			elif text == "start":
				if player == host_player:
					s = "(Game #" + str(game_id) + ") The game has started. Available actions: 'shoot', 'reload', 'defend', 'bang'"
					print(s)
					api.update_status(s)
					game = PlayGame()
				else:
					api.send_direct_message(user=player.id, text="Only the host player can start the game.")
			elif text in move_list.keys():
				game.get_reply(player,text)
	
	def on_error(self, status):
		print status
		
	def join_game(self, player):
		"""Join the game. Adds the given player to the player list."""
		if player in player_list:
			print(player.screen_name + " has already joined the game.")
		else:
			player_list.append(player)
			print(player.screen_name + " has joined the game.")
	
	def new_game(self):
		"""Starts a new game."""
		global game_id
		game_id = DataManager.get_last_game_id()
		game_id += 1
		DataManager.save_game_id(game_id)		
		api.update_status( "(Game #" + str(game_id) + ") A new game has been created. Send a direct message 'join' to join the game.")
		
class PlayGame:
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
	stream.userstream()
		
if __name__=="__main__":
	main()
	