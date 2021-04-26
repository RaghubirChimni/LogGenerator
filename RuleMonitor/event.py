class Event:

	def __init__(self, eventType, eventName, values, process_id):
		self.eventType = eventType
		self.eventName = eventName
		self.values = values
		self.process_id = process_id

	def __str__(self):
		result = self.eventName+'('
		for v in self.values:
			result += str(v) + ', '
		result = result[:-2]
		result += ")"

		return result