

class SongData(list):
	"""
		Holds a list of song data with a type label. (struct)

		I.e: SongData([ ... ], 'amplitude_time')
	"""

	def __init__(self, data, type):
		self.data = data
		self.type = type