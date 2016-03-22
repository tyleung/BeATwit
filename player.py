import tweepy

class Player:
	move = None
	qi = 0
	
	def __init__(self, user):
		self.user = user
		
	def get_id(self):
		return str(self.user['id'])
	
	def get_name(self):
		return str(self.user['name'])
	
	def get_screen_name(self):
		return str(self.user['screen_name'])