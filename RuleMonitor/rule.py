class Rule:

	def __init__(self, ruleName, bodyProcessAtoms, bodyGapAtoms, headProcessAtoms, headGapAtoms):
		self.ruleName = ruleName
		self.bodyProcessAtoms = bodyProcessAtoms
		self.bodyGapAtoms = bodyGapAtoms
		self.headProcessAtoms = headProcessAtoms
		self.headGapAtoms = headGapAtoms

		self.bodyVariables = []

		for a in bodyProcessAtoms:
			for v in a.variables:
				if v not in self.bodyVariables:
					self.bodyVariables.append(v)

		self.headVariables = []

		for a in headProcessAtoms:
			for v in a.variables:
				if v not in self.headVariables:
					self.headVariables.append(v)

	def __str__(self):
		result = "Rule: "+self.ruleName+'\n'
		result += "if\n"
		for a in self.bodyProcessAtoms+self.bodyGapAtoms:
			result += str(a)+"\n"
		result += "then\n"
		for a in self.headProcessAtoms+self.headGapAtoms:
			result += str(a)+'\n'
		result += 'end\n' 
		return result
