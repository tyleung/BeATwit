class Player:
	"""Defines a player in the game."""
	
	def __init__(self, user):
		self.id = str(user['id'])
		self.name = str(user['name'])
		self.screen_name = str(user['screen_name'])
		self.move = 0
		self.qi = 0
		self.reply = 0