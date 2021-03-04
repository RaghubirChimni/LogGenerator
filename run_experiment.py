# Raghubir Chimni
# 1/27/2021

from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from model_builder import ModelBuilder
import sys
import random
import numpy as np

# Usage: python run_experiment.py <mean> <standard_deviation> <file_name>
mean = int(sys.argv[1])
standard_deviation = int(sys.argv[2])
file_name = sys.argv[3]

sm = SimulationManager(start = datetime.now(), end = datetime.now() + timedelta(days=3))
# writes results into <filename>.txt
sm.simulate(file_name) 

# Gets file path and opens file
path = "output\\" + file_name + '.txt'
f = open(path)

#ordered output file
outfile = open("output\\" + file_name + "_ordered.txt", "w")

# list of names to pull from 
names = ['Alice', 'Bob', 'Jack', 'Lucy', 'Adam', 'Emily']

# keeps track of attributes for pid and line
name = ''
age = ''
addToLine = ''
splitLine = []

# how it orders the file by pid
for line in sorted(f, key=lambda line: int(line.split()[1])):
    splitLine = line.split()
    if(not 'START' in splitLine and not 'END' in splitLine):
        addToLine = ' Name=' + name
    elif('START' in splitLine or 'END' in splitLine): 
        if('START' in splitLine):
            name = random.choice(names) #get random name from names   
            age = str(int(np.random.normal(mean, standard_deviation))) # ages come from normal distribution
        addToLine=''
    
    if('check_faq' in splitLine or 'send_response' in splitLine or 'open_support' in splitLine):
        addToLine = addToLine + ' Age=' + age

    outfile.write(line.rstrip() + addToLine +'\n')

# close files
f.close()
outfile.close()