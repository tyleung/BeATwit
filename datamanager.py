game_id_file = "gameid.txt"

class DataManager:
	"""This class helps keeping all the ids saved in a txt file"""
	
	@staticmethod
	def save_game_id(id):
		"""Save current game ID to a file"""
		last_id = DataManager.get_last_game_id()

		if last_id < id:
			f = open(game_id_file, 'w')
			f.write(str(id)) # no trailing newline
			f.close()
		else:
			print('Received smaller ID, not saving. Old: %d, New: %s' % (last_id, id))

	@staticmethod
	def get_last_game_id():
		"""Retrieve last game ID from a file"""
		try:
			f = open(game_id_file, 'r')
			id = int(f.read())
			f.close()
		except IOError:
			print('IOError raised, returning zero (0)')
			return 0
		return id