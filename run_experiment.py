from datetime import datetime, timedelta
from simulation_manager import SimulationManager
import sys

#from data import DataManager

# Usage: python run_experiment.py <num_users> <database_size> <file_name>

num_users = int(sys.argv[1])
database_size = int(sys.argv[2])
file_name = sys.argv[3] + '.txt'

# making data lists
#users = [i for i in range(num_users)]
#database = [i for i in range(database_size)]
#data_manager = DataManager(database, users)

# Trying out simulation
sm = SimulationManager(start = datetime.now(), end = datetime.now() + timedelta(days=3))

sm.simulate(file_name) # writes results into filename.txt

# Gets file path and opens file
path = "output\\" + file_name
f = open(path)

#result = sum(f.rows)
#print (result)