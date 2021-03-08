class ProcessAtom:

	def __init__(self, processName, attributes, variables):
		self.processName = processName
		self.attributes = attributes
		self.variables = variables

	def __str__(self):
		result = self.processName+'('
		for i,a in enumerate(self.attributes[:-1]):
			result += a+": "+self.variables[i]+', '
		result = result[:-2]
		result += ')@'
		result += self.variables[-1]
		return result
