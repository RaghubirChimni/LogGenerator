class Event:

	def __init__(self, eventType, eventName, values):
		self.eventType = eventType
		self.eventName = eventName
		self.values = values

	def __str__(self):
		result = self.eventName+'('
		for v in self.values:
			result += str(v) + ', '
		result = result[:-2]
		result += ")"

		return result