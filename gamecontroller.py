class GameController:
	
	def get_player(user, player_list):
		"""Gets the player object from the player list given the user."""
		for p in player_list:
			if p.id == user['id']:
				return p
		return None
	
	def user_exists(user, player_list):
		"""Returns true if the user exists in the player list."""
		return any(p.id == str(user['id']) for p in player_list)
