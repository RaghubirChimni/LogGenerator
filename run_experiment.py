# Raghubir Chimni
# 1/27/2021

from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from model_builder import ModelBuilder
import sys


# Usage: python run_experiment.py <file_name>
#num_users = int(sys.argv[1])
#database_size = int(sys.argv[2])
file_name = sys.argv[1]

sm = SimulationManager(start = datetime.now(), end = datetime.now() + timedelta(days=3))

sm.simulate(file_name) # writes results into <filename>.txt

# Gets file path and opens file
path = "output\\" + file_name + '.txt'
f = open(path)

#ordered output file
outfile = open("output\\" + file_name + "_ordered.txt", "w")

# how it orders the file by pid
for line in sorted(f, key=lambda line: int(line.split()[1])):
    outfile.write(line)

# closes files
f.close()
outfile.close()