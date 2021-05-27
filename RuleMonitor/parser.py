from .event import Event
from .rule import Rule
from .assignment import Assignment
from .processatom import ProcessAtom
from .gapatom import GapAtom

import csv
import random

def read_eventstream_from_csv(eventStreamCSVFileName):
		eventStream = []

		with open(eventStreamCSVFileName, newline='') as f:
			reader = csv.reader(f)
			for d in list(reader):
				if not d:
					continue
				eventType = d[0]
				eventName = d[1]
				eventData = list(map(lambda y: y.strip(), d[2:]))
				eventData[-1] = int(eventData[-1])
				eventStream.append(Event(eventType, eventName, eventData))

		return eventStream

# used with the output format of Gabriel's workflow simulator
def read_eventstream_from_txt(eventstream_txt_filename):
	eventstream = []

	with open(eventstream_txt_filename, 'r') as f:
		for d in f.readlines():
			d = d.strip()
			d_list = d.split(' ')

			process_id = d[1]

			if d[3]=="START" or d[3]=="END":
				event_type = d[3]
				event_data = []
			else:
				event_type = "activity"
				event_data = list(map(lambda y: y.split("=")[1], d_list[4:]))
			
			event_time = int(d_list[0])
			event_name = d_list[3]
			
			event_data.append(event_time)
			eventstream.append(Event(event_type, event_name, event_data, process_id))

	return eventstream

def generate_random_rule_with_fixed_process_atoms(number_body_process_atoms, number_head_process_atoms):

	ruleName = "Random Rule"

	number_body_gap_atoms = random.randint(1,3)
	number_head_gap_atoms = random.randint(1,3)
	
	bodyProcessAtoms = []
	bodyGapAtoms = []
	headProcessAtoms = []
	headGapAtoms = []

	bodyProcessAtomsStrings = [
	"request(support a, value d, class b, name c)@x",
	"schedule(support a, name c)@y",
	"compute(support a, name c)@z"][:number_body_process_atoms]

	bodyVariables = ["x","y","z"][:number_body_process_atoms]

	for b in bodyProcessAtomsStrings:
		bodyProcessAtoms.append(parseProcessAtomString(b))

	headProcessAtomsStrings = [
	"payment(support a, name c)@t",
	"receipt(support a, name c)@s"][:number_head_process_atoms]

	for h in headProcessAtomsStrings:
		headProcessAtoms.append(parseProcessAtomString(h))

	headVariables = ["t","s"][:number_head_process_atoms]

	for _ in range(number_body_gap_atoms):

		var1 = random.choice(bodyVariables)
		var2 = random.choice(bodyVariables)
		gap = random.randint(0,100)
		direction = random.choice(["<=",">="])

		line = var1+"+"+str(gap)+" "+direction+" "+var2
		
		bodyGapAtoms.append(parseGapAtomString(line))

	for _ in range(number_head_gap_atoms):
		var1 = random.choice(headVariables)
		var2 = random.choice(headVariables+headVariables)
		gap = random.randint(0,100)
		direction = random.choice(["<=",">="])

		line = var1+"+"+str(gap)+" "+direction+" "+var2
		
		headGapAtoms.append(parseGapAtomString(line))

	for var1 in bodyVariables:
		for var2 in headVariables:
			gap = 500
			direction = ">="

			line = var1+"+"+str(gap)+" "+direction+" "+var2

			headGapAtoms.append(parseGapAtomString(line))

	r = Rule(ruleName, bodyProcessAtoms, bodyGapAtoms, headProcessAtoms, headGapAtoms)

	#print(r)

	return r

def without(l,e):
	l.remove(e)
	return l

def generate_random_rule():

	ruleName = "Random Rule"

	number_body_process_atoms = random.randint(1,4)
	number_head_process_atoms = random.randint(1,2)
	number_body_gap_atoms = random.randint(1,3)
	number_head_gap_atoms = random.randint(1,3)
	
	bodyProcessAtoms = []
	bodyGapAtoms = []
	headProcessAtoms = []
	headGapAtoms = []

	bodyProcessAtomsStrings = [
	"request(support a, value d, class b, name c)@x",
	"schedule(support a, name c)@y",
	"compute(support a, name c)@z"][:number_body_process_atoms]

	bodyVariables = ["x","y","z"][:number_body_process_atoms]

	for b in bodyProcessAtomsStrings:
		bodyProcessAtoms.append(parseProcessAtomString(b))

	headProcessAtomsStrings = [
	"payment(support a, name c)@t",
	"receipt(support a, name c)@s"][:number_head_process_atoms]

	for h in headProcessAtomsStrings:
		headProcessAtoms.append(parseProcessAtomString(h))

	headVariables = ["t","s"][:number_head_process_atoms]

	# random gap atoms in head
	if len(bodyVariables)>1:

		for _ in range(number_body_gap_atoms):

			var1 = random.choice(bodyVariables)
			bodyVariablesWithout = list(bodyVariables)
			bodyVariablesWithout.remove(var1)
			var2 = random.choice(bodyVariablesWithout)
			gap = random.randint(0,100)
			direction = random.choice(["<=",">="])

			line = var1+"+"+str(gap)+" "+direction+" "+var2
			
			bodyGapAtoms.append(parseGapAtomString(line))

	# random gap atoms in head
	if len(headVariables)>1:

		for _ in range(number_head_gap_atoms):
			var1 = random.choice(headVariables)
			headVariablesWithout = list(headVariables)
			headVariablesWithout.remove(var1)
			var2 = random.choice(bodyVariables+headVariables)
			gap = random.randint(0,100)
			if var2 in bodyVariables:
				direction = ">="
			else:
				direction = random.choice(["<=",">="])

			line = var1+"+"+str(gap)+" "+direction+" "+var2
			
			headGapAtoms.append(parseGapAtomString(line))

	# gap atoms to ensure rule is reasonable
	for var1 in bodyVariables:
		bodyVariablesWithout = list(bodyVariables)
		bodyVariablesWithout.remove(var1)
		for var2 in bodyVariablesWithout:
			gap = 100
			direction = ">="

			line = var1+"+"+str(gap)+" "+direction+" "+var2

			bodyGapAtoms.append(parseGapAtomString(line))

	# gap atoms to ensure rule is bounded
	for var2 in headVariables:
		var1 = random.choice(bodyVariables)
		gap = 100
		direction = ">="

		line = var1+"+"+str(gap)+" "+direction+" "+var2

		headGapAtoms.append(parseGapAtomString(line))

	r = Rule(ruleName, bodyProcessAtoms, bodyGapAtoms, headProcessAtoms, headGapAtoms)
	
	#print(r)

	return r


def readRuleFromTxtFile(ruleTxtFile):

	file1 = open(ruleTxtFile, 'r')
	
	lines = file1.read().splitlines()

	file1.close()

	lines.pop(0) # consume "Rule"

	ruleName = lines.pop(0) # get rule name

	lines.pop(0) # consume "if"		
	
	line = lines.pop(0) # get first line after if
	
	bodyProcessAtoms = []
	bodyGapAtoms = []
	headProcessAtoms = []
	headGapAtoms = []

	while(line != 'then'):
		if ("<" in line or "=" in line or ">" in line):
			bodyGapAtoms.append(parseGapAtomString(line))
		else:
			bodyProcessAtoms.append(parseProcessAtomString(line))
		line = lines.pop(0)

	lines.pop() # remove "end"

	for line in lines:
		if ("<" in line or "=" in line or ">" in line):
			headGapAtoms.append(parseGapAtomString(line))
		else:
			headProcessAtoms.append(parseProcessAtomString(line))

	r = Rule(ruleName, bodyProcessAtoms, bodyGapAtoms, headProcessAtoms, headGapAtoms)
	return r

def parseProcessAtomString(s):
	name = s[:s.find("(")]
	dataString = s[s.find('(')+1:s.find(')')]
	attributes = []
	variables = []
	for d in dataString.split(','):
		data = d.strip().split(" ")
		attributes.append(data[0])
		variables.append(data[1])
	attributes.append('time')
	variables.append(s[s.find('@')+1:])

	return ProcessAtom(name, attributes, variables)


def parseGapAtomString(s):
	lhs = ''
	rhs = ''
	gap = 0
	direction = ''
	offset = 0

	if '<=' in s:
		direction = '<='
		offset = 1
	elif '>=' in s:
		direction = '>='
		offset = 1
	elif '>' in s:
		direction = '>'
	elif '<' in s:
		direction = '<'
	elif "=" in s:
		direction = '='
	else:
		print("Operator not recognized")

	rhs = s[s.find(direction)+offset+1:].strip()

	if (s.find('+') != -1):
		lhs = s[:s.find('+')][:s.find(direction)].strip()
		gap = s[s.find('+')+1:s.find(direction)-1]
	else:
		lhs = s[:s.find(direction)].strip()

	return GapAtom(lhs, rhs, direction, 'days', int(gap))

