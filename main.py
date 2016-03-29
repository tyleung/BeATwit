import json
import tweepy
from datamanager import DataManager
from gamecontroller import GameController as gc
from player import Player

CONSUMER_KEY = "KKbGVz0PwPxkSD6LN8Qj75OkC"
CONSUMER_SECRET = "E8CmIICmbCmf822b4SaQJzLctwuAOyThOe6xpodJ1zNKWllM2B"
ACCESS_TOKEN = "607777499-NN5EAVStoLU36K1J2HGYVyJmGkiEovP4dgruM8o6"
ACCESS_TOKEN_SECRET = "W7eXOTb1JtSk6vr3Uzvww8UXsqp2umw53ZgQevVRNnGAG"
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

game_id = 0
host_player = Player()
move_list = {"shoot": 0, "reload": 1, "defend": 2, "bang": 3}
player_list = []

class TweetListener(tweepy.StreamListener):
	
	def __init__(self):
		super(TweetListener, self).__init__()
		self.game_created = False
		self.game = None
		
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
				s = "(Game #" + str(game_id) + ") You are the host player. Send 'start' to start the game when everyone has joined."
				api.send_direct_message(user=player.id, text=s)
				print(s)
				self.game_created = True
		else:
			if text == "join":
				self.join_game(player)
			elif text == "start":
				if player == host_player:
					s = "(Game #" + str(game_id) + ") The game has started. Available actions: 'shoot', 'reload', 'defend', 'bang'"
					print(s)
					api.update_status(s)
					self.game = PlayGame()
				else:
					api.send_direct_message(user=player.id, text="Only the host player can start the game.")
			elif text in move_list.keys():
				self.game.get_reply(player, text)
	
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
		m = "(Game #" + str(game_id) + ") A new game has been created. Send a direct message 'join' to join the game."
		api.update_status(m)
		print(m)
		
class PlayGame:
	global player_list
	def __init__(self):
		self.player_num = len(player_list)
		self.count_reply = 0
		self.gameover_list =[]
		self.gameround = 1

	def get_reply(self,who,reply):
		#print(player_list)
		self.count_reply+=1
		#check if the player replied
		idx = [p.id for p in player_list].index(who.id)
		player_list[idx].reply = 1
		print("check if player replied")
		#0:reload, 1:shoot,2:defend,3:bang
		
		
		if reply == "shoot":
			if player_list[idx].qi == 0:
				#send direct msg here. by default = set to reload.
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") Aww! You don't have any bullet! Set to reload by default!"
				api.send_direct_message(user=player_list[idx].id ,text=m)				
				print(m)
				player_list[idx].move = 0
				player_list[idx].reply = 0
			else:
				player_list[idx].move = 1
				player_list[idx].qi -= 1
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") You pulled the trigger! We will see... Please wait."
				api.send_direct_message(user=player_list[idx].id ,text=m)
				print(m)
		elif reply == "reload":
			player_list[idx].move = 0
			player_list[idx].qi += 1
			m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") You reloaded the gun! Now you have one more bullet, let's see if you can survive this round. Please wait."
			api.send_direct_message(user=player_list[idx].id ,text=m)
			print(m)
		elif reply == "defend":
			player_list[idx].move = 2
			m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") You chose to defend! Hopefully you will survive this round :)"
			api.send_direct_message(user=player_list[idx].id ,text=m)
			print(m)
		elif reply == "Bang":
			if player_list[idx].qi < 3 :
				#send direct msg here. by default set to reload.
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") Aww! You don't have enough bullets! Set to reload by default!"
				api.send_direct_message(user=player_list[idx].id ,text=m)			
				print(m)
				player_list[idx].move = 0
				player_list[idx].reply = 0
			else:
				player_list[idx].move = 3			
				player_list[idx].qi -= 3
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") You pulled out the shotgun and pulled the trigger! Let's see if you get lucky shoot! Please wait."
				api.send_direct_message(user=player_list[idx].id ,text=m)				
				print(m)
		if self.count_reply == self.player_num:
			result = self.get_result()
		
		
	def get_result(self):
		print(player_list)
		global game_id
		#the attack 
		for player in player_list:
			#Bang attack. Undefendable
			if player.move == 3:
				for player2 in player_list:
					if player2.move != 3:
						if player2 not in self.gameover_list:
							self.gameover_list.append(player2)
				sn = player.screen_name
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") @%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.send_direct_message(user=player.id ,text=m)
				print(m)
			#normal attack, defendable

			elif player.move == 1:
				for player2 in player_list:
					if player2.move == 0:
						if player2 not in self.gameover_list:
							self.gameover_list.append(player2)
				sn = player.screen_name
				m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") @%s Wow! looks like you killed somebody. Nice move!"%(sn)
				api.send_direct_message(user=player.id ,text=m)
				print(m)
		#nobody attack, then everyone is safe
		print(self.gameover_list)
		if self.gameover_list ==[]:
			for player in player_list:
				m = "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") Looks like everyone is safe this round! What about your next move?"
				api.send_direct_message(user=player.id ,text=m)
			#print(m)
		#send msg to the dead men	
		for player in self.gameover_list:
			sn = player.screen_name
			m =  "(Game #" + str(game_id) + ")(Round "+ str(self.gameround) +") @%s I'm sorry,you've been eliminated in this round..."%(sn)
			api.send_direct_message(user=player.id ,text=m)
			print(m)
			player_list.remove(player)
		#reset the moves to reload
		for player in player_list:
			player.move = 0
		
		
		self.gameover_list = []
		self.count_reply = 0
		self.player_num = len(player_list)
		self.gameround += 1
		
		#end the game
		if len(player_list) == 1:
			player = player_list[0]
			sn = player.screen_name
			m =  "(Game #" + str(game_id) + ") @%s Nicely done! You are the winner of this game!"%(sn)
			api.update_status(m,player.id)
			#print(m)
			
	
	
def main():
	l = TweetListener()
	stream = tweepy.Stream(auth=api.auth, listener=l)
	stream.userstream()
		
if __name__=="__main__":
	main()
	