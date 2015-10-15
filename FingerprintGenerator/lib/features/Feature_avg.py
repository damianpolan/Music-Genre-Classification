
import Feature

class Feature_avg(Feature):
	"""
	Implementation of Feature. 

	USES: amplitude vs time data.
	"""

	def __init__(self, data, fromRaw=False):
		self.average = 0;

		for sample in data:
			self.average += sample[0] + sample[1];

		self.average /= len(data) * 2;
		
		
	def toRaw(self):
		return self.average;

	
