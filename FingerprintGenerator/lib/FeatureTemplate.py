

class Feature(object):
	"""
	Feature is an abstract template class. Should be seperately implemented.
	"""

	#CONSTRUCTOR
	def __init__(self, data):
		raise "Class not implemented. Feature is an abstract class.";   
		pass


	def toRaw(self):
		raise "Class not implemented. Feature is an abstract class.";


	@staticmethod
	def fromRaw(rawCharData):
		raise "Must be implemented in child class.";
