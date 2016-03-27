class Player:
	"""Defines a player in the game."""
	
	def __init__(self, user=None):
		if user != None:
			self.id = user['id']
			self.name = user['name']
			self.screen_name = user['screen_name']
		self.move = 0
		self.qi = 0
		self.reply = 0
		
	def __eq__(self, other):
		return self.id == other.id
		
	def __repr__(self):
		return str(self.__dict__)