from .event import Event
from .rule import Rule
from .assignment import Assignment
from .parser import *
import pdb
import copy
import time

class Monitor:
	def __init__(self, monitorName, rule_file_path):
		self.name = monitorName
		self.ruleVector = [readRuleFromTxt(rule_file_path)]
		self.assignmentVector = []
		self.currentTime = 0  

	def reset(self):
		self.assignmentVector = []
		self.currentTime = 0		

	def monitoringLoop(self, eventstream_file_path):

		eventstream = read_eventstream_from_txt(eventstream_file_path)

		eventstream_length = len(eventstream)

		userMode = 'normal'

		userInput = 'n'

		start = time.time()

		timesOfActs = []

		startAct = 0
		prevAct = 0

		i=0

		while ((userInput != 'q') and (i < eventstream_length)):
			
			if userInput == 'q':
				break

			if userInput == 'a':
				self.printAssignments()

			if userInput == 'm':
				for r in self.ruleVector:
					self.findMatches(r)

			if userInput == 'n':

				'''
				input()

				print("number of assigments",len(self.assignmentVector))
				self.printAssignments()
				'''

				if eventstream[i].eventType == "process":
					if i % 100 == 0 and i != 0:
						startAct = time.time()
						timesOfActs.append(startAct - prevAct)
						prevAct = startAct
						
					self.handleProcessEvent(eventstream[i])					
					
					for r in self.ruleVector:
						self.findMatches(r)

					batch_size = 1

					if i%batch_size == 0:
						self.removeExpiredData(eventstream[i])

					i += 1

			if userInput == 'x':
				self.removeExpiredData(eventstream[i])

			#userInput = raw_input()

		end = time.time()

		number_of_violations = 0
		output_string = ""
		for a in self.assignmentVector:
			if a.typeOfAssignment == 'body':
				if a.complete:
					if len(a.missingProcessAtoms) == 0:
						if len(a.matchingAssignments) == 0:
							output_string += "Unmatched Body Assignment: \n"+str(a)+"\n"
							number_of_violations += 1
						else:
							output_string += "Matched Body Assignment: \n"+str(a)+"\n"

		output_string = "Number of Violations: "+str(number_of_violations)+"\n"+output_string[:-2]

		output_string = "Number of Violations: "+str(number_of_violations)

		return self.assignmentVector, output_string, (end-start), timesOfActs

	def handleProcessEvent(self, e: Event):

		newAssignments = []

		for rule in self.ruleVector:

			# Check if event is relevant in the rule body
			for bodyProcessAtom in rule.bodyProcessAtoms:
				if (e.eventName == bodyProcessAtom.processName):
					
					# Create new body assignment
					variablesDefinedFlags = {x:False for x in rule.bodyVariables}

					values = {}
					for i,v in enumerate(bodyProcessAtom.variables):
						values[v] = e.values[i]
						variablesDefinedFlags[v]=True

					seenProcessAtoms = [];
					seenProcessAtoms.append(bodyProcessAtom)

					missingProcessAtoms = []
					for ruleBodyProcessAtom in rule.bodyProcessAtoms:
						if bodyProcessAtom != ruleBodyProcessAtom:
							missingProcessAtoms.append(ruleBodyProcessAtom)

					matchingAssignments = []

					new_body_assignment = Assignment(rule.bodyVariables,
					values,variablesDefinedFlags,"body",
					rule, missingProcessAtoms,seenProcessAtoms,[],[e])

					self.assignmentVector.append(new_body_assignment)
					newAssignments.append(new_body_assignment)

			# Check if event is relevant in the rule head

			for headProcessAtom in rule.headProcessAtoms:
				if (e.eventName == headProcessAtom.processName):
					
					# create new head assignment
					variablesDefinedFlags = {x:False for x in rule.headVariables}

					values = {}
					for i,var in enumerate(headProcessAtom.variables):
						values[var] = e.values[i]
						variablesDefinedFlags[var]=True

					seenProcessAtoms = [];
					seenProcessAtoms.append(headProcessAtom)

					missingProcessAtoms = []
					for ruleHeadProcessAtom in rule.headProcessAtoms:
						if headProcessAtom != ruleHeadProcessAtom:
							missingProcessAtoms.append(ruleHeadProcessAtom)

					matchingAssignments = []

					new_head_assignment = Assignment(rule.headVariables,
					values,variablesDefinedFlags,"head",
					rule, missingProcessAtoms,seenProcessAtoms,[],[e])

					self.assignmentVector.append(new_head_assignment)
					newAssignments.append(new_head_assignment)

			# loop through existing assignment vector
			# searching for assignments this event will extend
			for assignment in self.assignmentVector:
				assignmentDefinedVariables = []

				for var in assignment.variables:
					if assignment.variablesDefinedFlags[var]:
						assignmentDefinedVariables.append(var)

				for missingAtom in assignment.missingProcessAtoms:
					if (e.eventName == missingAtom.processName):
						eventValuesForVariables = {}

						for i,var in enumerate(missingAtom.variables):
							eventValuesForVariables[var] = e.values[i]

						match = True

						for var in missingAtom.variables:
							if assignment.variablesDefinedFlags[var]:
								if (assignment.values[var] != eventValuesForVariables[var]):
									match = False;
									break;
						
						if not match:
							continue;

						if assignment.typeOfAssignment == "body":
							constraints = assignment.rulePointer.bodyGapAtoms
						else:
							constraints = assignment.rulePointer.headGapAtoms

						mergedMap = assignment.values.copy()

						for var in eventValuesForVariables.keys():
							if not var in assignmentDefinedVariables:
								assignmentDefinedVariables.append(var)
							mergedMap[var] = eventValuesForVariables[var]

						# check if new assignment is consistent with assignment of interest
						consistentWithGapAtoms = True

						for constraint in constraints:
							if ((constraint.lhs in mergedMap.keys()) and
							(constraint.rhs in mergedMap.keys())):
								if not constraint.checkTruthValueWithAssignment(mergedMap):
									consistentWithGapAtoms = False

						if consistentWithGapAtoms:
							b = copy.deepcopy(assignment)
							
							for var in mergedMap.keys():
								b.values[var] = mergedMap[var]
								b.variablesDefinedFlags[var] = True

							for x in b.missingProcessAtoms:
								if str(x)==str(missingAtom):
									b.missingProcessAtoms.remove(x) 

							b.seenProcessAtoms.append(missingAtom)

							b.seenEvents.append(e)

							b.complete = len(b.missingProcessAtoms)==0

							b.expirationTime = b.computeExpirationTime()

							self.assignmentVector.append(b)
		
		return newAssignments

	def findMatches(self, r: Rule):
		
		# using body assignment b, find matching head assignment h
		for b in self.assignmentVector:
			if ((b.rulePointer.ruleName == r.ruleName) and (b.complete) and b.typeOfAssignment == 'body'):
				
				for h in self.assignmentVector:
					if ((h.rulePointer.ruleName == r.ruleName) and (h.typeOfAssignment == 'head') and (h.complete) and h not in b.matchingAssignments):
						if(self.doAssignmentsMatch(b,h)):

							# found a match
							b.matchingAssignments.append(h)

	def expired(self, a: Assignment):
		return a.expirationTime < self.currentTime
		
	# Removing data that expires before time of event e
	def removeExpiredData(self, e: Event):
		
		latestEventTime = int(e.values[-1])

		unexpiredData = []
		expiredData = []

		for a in self.assignmentVector:
			if latestEventTime <= a.expirationTime:
				unexpiredData.append(a)
			else:
				expiredData.append(a)

		self.assignmentVector = unexpiredData

	def printAssignments(self):
		for i,a in enumerate(self.assignmentVector):
			print("assignmentVector["+str(i)+"]")
			print(a)

	def doAssignmentsMatch(self, a, b):
		for v in a.variables:
			if v in b.variables:
				if (a.values[v] != b.values[v]):
					return False

		mergedMap = a.values.copy()

		for k,v in b.values.items():
			mergedMap[k] = v

		constraints = []

		if (a.typeOfAssignment == 'body'):
			constraints += a.rulePointer.bodyGapAtoms
			constraints += b.rulePointer.headGapAtoms
		else:
			constraints += a.rulePointer.headGapAtoms
			constraints += b.rulePointer.bodyGapAtoms
		
		for c in constraints:
			if (not c.checkTruthValueWithAssignment(mergedMap)):
				return False

		return True












