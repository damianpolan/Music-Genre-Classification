

class Feature(object):
	"""
	Feature is an abstract template class. Should be seperately implemented.
	"""

    

	#CONSTRUCTOR
	def __init__(self, data):
        # defines the feature data this feature implementation will use. In the case it is None, raw time domain data will be used. Otherwise, data will be another Feature object.
        self.inputFeature = None 
		raise "Class not implemented. Feature is an abstract class.";   
		pass



	def toRaw(self):
		raise "Class not implemented. Feature is an abstract class.";
