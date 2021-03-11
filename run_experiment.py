# Raghubir Chimni
# 1/27/2021

from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from model_builder import ModelBuilder
from RuleMonitor.monitor import Monitor
import RuleMonitor.parser
import sys
import random
import numpy as np
import time

def create_eventstream_from_simulator(mean, standard_deviation, simulator_output_file_name):
    
    sm = SimulationManager(start = datetime.now(), end = datetime.now() + timedelta(days=3))
    # writes results into <filename>.txt
    sm.simulate(simulator_output_file_name) 

    # Get file path for output of simulation
    # Use sys.platform to disginguish between Mac OS / Windows
    if sys.platform == "darwin":
        path = "output/" + simulator_output_file_name + '.txt'
    else:
        path = "output\\" + simulator_output_file_name + '.txt'

    #Opens file to write simulator output
    f = open(path)

    ordered_file_path = ""

    # Open file to write ordered output into
    if sys.platform == "darwin":
        ordered_file_path = "output/" + simulator_output_file_name + "_ordered.txt"
    else:
        ordered_file_path = "output\\" + simulator_output_file_name + "_ordered.txt"

    outfile = open(ordered_file_path, "w")

    # list of names to pull from 
    names = ['Alice', 'Bob', 'Charlie', 'David', 'Emily', 'Frank']

    # keeps track of attributes for pid and line
    name = ''
    age = ''
    addToLine = ''
    splitLine = []

    # how it orders the file by pid
    for line in sorted(f, key=lambda line: int(line.split()[1])):
        line = line[:line.index("#")-1] # remove '#' and everything beyond
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

    return ordered_file_path

if __name__ == "__main__":

    rule_file_name = sys.argv[1]

    if sys.platform == "darwin":
        rule_file_path = "examples/" + rule_file_name
    else:
        rule_file_path = "examples\\" + rule_file_name
    
    simulator_output_file_name = sys.argv[2]

    eventstream_file_path = ""

    create_new_file = True

    if create_new_file:
        mean = 10
        standard_deviation = 5
        eventstream_file_path = create_eventstream_from_simulator(mean, standard_deviation, simulator_output_file_name)
    
    m = Monitor("MyMonitor", rule_file_path)

    average = 0
    number_of_runs = 4

    for i in range(number_of_runs):
        assignment_vector, output_string, time_to_monitor = m.monitoringLoop(eventstream_file_path)
        m.reset()
        print("\n"+20*'-')
        print("\nTrial "+str(i)+": "+str(time_to_monitor)+" seconds")
        print(output_string)
        average += time_to_monitor

    print("\nExperiment Summary")
    print("rule:", rule_file_path)
    print("event_stream:", eventstream_file_path)
    print("Average run time:", average/number_of_runs)



