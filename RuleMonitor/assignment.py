class Assignment:

	def __init__(self, variables, values, variablesDefinedFlags, typeOfAssignment, rulePointer, missingProcessAtoms, seenProcessAtoms, matchingAssignments, seenEvents):

		self.variables = variables
		self.variablesDefinedFlags = variablesDefinedFlags
		self.values = values

		self.rulePointer = rulePointer
		self.typeOfAssignment = typeOfAssignment

		self.missingProcessAtoms = missingProcessAtoms
		self.seenProcessAtoms = seenProcessAtoms
		self.seenEvents = seenEvents
		self.matchingAssignments= matchingAssignments
		self.complete = len(missingProcessAtoms)==0
		self.matched = len(matchingAssignments)!=0 

		self.expirationTime = self.computeExpirationTime()

	def computeExpirationTime(self):

		# TO DO: replace the high/low calculations with a symbolic package

		constraints = []

		if ((not self.complete) and self.typeOfAssignment=='body'):
			constraints = self.rulePointer.bodyGapAtoms
		elif (self.typeOfAssignment=='head'):
			constraints = self.rulePointer.headGapAtoms
		else:
			constraints = self.rulePointer.headGapAtoms
			constraints += self.rulePointer.bodyGapAtoms

		timeVariables = []
		for c in constraints:
			if not c.lhs in timeVariables:
				timeVariables.append(c.lhs)
			if not c.rhs in timeVariables:
				timeVariables.append(c.rhs)

		lowest = {}
		highest = {}

		currentTime = 0
		lastTime = 10000

		# initialize higher and lower bounds for unknown variables
		for v in timeVariables:
			if v in self.variablesDefinedFlags.keys():
				if self.variablesDefinedFlags[v]:
					lowest[v] = self.values[v]
					highest[v] = self.values[v]
					currentTime = max(self.values[v],currentTime)
				else:
					lowest[v] = currentTime
					highest[v] = lastTime
			else:
				lowest[v] = currentTime
				highest[v] = lastTime

		# replace this with symbolic variable elimination?
		
		earliestExpirationTime = lastTime
		
		for _ in range(len(constraints)):
			for c in constraints:

				offset = 0

				# c.lhs + gap </<= c.rhs
				if ("<" in c.direction):
					if c.direction=="<":
						offset += 1

					lowest[c.rhs] = max(lowest[c.rhs],lowest[c.lhs]+c.gap+offset)

					highest[c.lhs] = min(highest[c.lhs],highest[c.rhs]-c.gap-offset)

				# c.lhs + gap >/>= c.rhs
				if (">" in c.direction):

					if c.direction==">":
						offset += 1

					lowest[c.lhs] = max(lowest[c.lhs],lowest[c.rhs]-c.gap+offset)

					highest[c.rhs] = min(highest[c.rhs],highest[c.lhs]+c.gap-offset)

				# c.lhs + gap == c.rhs
				if (c.direction=="="):
					
					if c.lhs in self.variablesDefinedFlags.keys():
						if self.variablesDefinedFlags[c.lhs]:
							lowest[c.rhs] = self.values[c.lhs] + c.gap
							highest[c.rhs] = self.values[c.lhs] + c.gap

					if c.rhs in self.variablesDefinedFlags.keys():
						if self.variablesDefinedFlags[c.rhs]:
							lowest[c.lhs] = self.values[c.rhs] - c.gap
							highest[c.lhs] = self.values[c.rhs] - c.gap

		for v in timeVariables:
			if v not in self.variablesDefinedFlags.keys():
				earliestExpirationTime = min(earliestExpirationTime, highest[v])
			if v in self.variablesDefinedFlags.keys() and not self.variablesDefinedFlags[v]:
					earliestExpirationTime = min(earliestExpirationTime, highest[v])

		return earliestExpirationTime

	def __str__(self):
		result = ''
		#result = "Assignment\n"
		#result += "rule: "+self.rulePointer.ruleName+', '
		#result += "type: "+self.typeOfAssignment+', '
		#result += "complete: "+str(self.complete)+'\n'
		result += "expirationTime: "+str(self.expirationTime)+'\n'
		if not self.complete:
			result += "values: "
			for v in self.variables:
				if self.variablesDefinedFlags[v]:
					result += v+"="+str(self.values[v])+', '
				else:
					result += v+"=undef"+', '

			result = result[:-2]
			result += '\n'
		else:
			result += str(self.values)
			result += '\n'

		#result += "expiration time: "+str(self.expirationTime)+'\n'
		'''
		result += "seenProcessAtoms: "
		for s in self.seenProcessAtoms:
			result += str(s)+', '
		if len(self.seenProcessAtoms)==0:
			result += "None\n"
		else:
			result = result[:-2]
			result += '\n'

		result += "seenEvents: "
		for s in self.seenEvents:
			result += str(s)+', '
		if len(self.seenEvents)==0:
			result += "None\n"
		else:
			result = result[:-2]
			result += '\n'
		
		result += "missingProcessAtoms: "
		for m in self.missingProcessAtoms:
			result += str(m)+', '
		if len(self.missingProcessAtoms)==0:
			result += "None\n"
		else:
			result = result[:-2]
			result += "\n"
		'''
		result += "Matching Head Assignments: "
		for m in self.matchingAssignments:
			result += str(m.values)+', \n'
		if len(self.matchingAssignments)==0:
			result += "None\n"
		else:
			result = result[:-2]
			result += '\n'

		return result


				





		








