import tweepy

class Player:
	"""Defines a player in the game."""
	
	def __init__(self, user):
		self.user = user
		self.id = str(user['id'])
		self.name = str(user['name'])
		self.screen_name = str(user['screen_name'])
		self.move = None
		self.qi = 0