class GapAtom:

	def __init__(self, lhs, rhs, direction, units, gap):
		self.lhs = lhs
		self.rhs = rhs
		self.direction = direction
		self.units = units
		self.gap = gap

	def __str__(self):
		return self.lhs+" + "+str(self.gap)+" "+self.direction+" "+self.rhs

	def checkTruthValueWithAssignment(self, a):
		l = self.lhs
		gap = self.gap
		r = self.rhs

		if (self.direction == "<"):
			return a[l]+gap < a[r]
		elif (self.direction == "<="):
			return a[l]+gap <= a[r]
		elif (self.direction == ">"):
			return a[l]+gap > a[r]
		elif (self.direction == ">="):
			return a[l]+gap >= a[r]
		elif (self.direction == "="):
			return a[l]+gap == a[r]
		else:
			print("ERROR: gap atom direction operator not recognized")

		return false