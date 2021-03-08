
class Constraint:

	def __init__(self, lhs: string, rhs: string, numerality: string, units: string, gap: int):
    self.lhs = lhs;
    self.rhs = rhs;
    self.numerality = numerality;
    self.units = units;
    self.gap = gap;
