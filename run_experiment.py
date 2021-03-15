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

# Given a filename, calculate the average concurrency, i.e. how many activities are active when an activity starts
def calculate_concurrency(filename):

    f = open(filename,'r')

    # calculate concurrency
    unfinished_activites = 0
    count_activities = 0
    total_overlaps = 0
    for line in f.readlines():
        if('START' in line):
            count_activities += 1
            total_overlaps += unfinished_activites
            unfinished_activites += 1
        elif('END' in line):
            unfinished_activites -= 1
    
    average_concurrency = total_overlaps/count_activities

    f.close()
    return average_concurrency

def create_eventstream_from_simulator(simulator_file_name, number_activities, number_data_elements):
    
    # simulator generates ~950 activites per day
    simulated_days = number_activities/950

    simulator_file_name = simulator_file_name + "_" + str(number_activities) + "_" + str(number_data_elements)

    sm = SimulationManager(start = datetime.now(), end = datetime.now() + timedelta(days=simulated_days))
    # writes results into <filename>.txt

    sm.simulate(name=simulator_file_name,resource_limit={'support': 30, 'trust': 30}) 

    # Get file path for output of simulation
    # Use sys.platform to disginguish between Mac OS / Windows
    if sys.platform == "darwin":
        simulator_output_path = "output/" + simulator_file_name + '.txt'
    else:
        simulator_output_path = "output\\" + simulator_file_name + '.txt'

    #Opens file to read simulator output
    f = open(simulator_output_path)

    number_simulated_activities = sum(1 for line in open(simulator_output_path))

    average_overlap = calculate_concurrency(simulator_output_path)
    print("average_overlap in simulation:",str(average_overlap))

    ordered_file_path = ""

    # Open file to write ordered output into
    if sys.platform == "darwin":
        ordered_file_path = "output/" + simulator_file_name + "_" + str(number_simulated_activities) + "_" + str(number_data_elements) + "_ordered.txt"
    else:
        ordered_file_path = "output\\" + simulator_file_name + "_" + str(number_simulated_activities) + "_" + str(number_data_elements) + "_ordered.txt"

    outfile = open(ordered_file_path, "w")

    data_elements = ["Name","City","University","Gender","Income"]

    # list of data elements to pull from 
    names = ['Alice', 'Bob', 'Charlie', 'David', 'Emily', 'Frank']
    cities = ['Boston', "Miami", "Seattle", "Chicago"]
    universities = ["UCSB", "Berkeley", "UT", "MIT"]
    genders = ["M", "F", "X"]
    incomes = [str(x) for x in range(1000,1200)]

    data_element_lists = [names,cities,universities,genders,incomes]

    sampled_data = {}

    activity_data = {}

    addToLine = ''
    splitLine = []

    # for line in sorted(f, key=lambda line: int(line.split()[1])):
    for line in f.readlines():
        line = line[:line.index("#")-1] # remove '#' and everything beyond
        splitLine = line.split()

        activity_instance_id = splitLine[1]

        if activity_instance_id not in activity_data.keys():
            for i in range(number_data_elements):
                sampled_data[data_elements[i]] = random.choice(data_element_lists[i])
            # age = str(int(np.random.normal(mean, standard_deviation))) # ages come from normal distribution
            
            addToLine=''
            for i, (k,v) in enumerate(sampled_data.items()):
                addToLine = addToLine + ' ' + k + '=' + v

            activity_data[activity_instance_id] = addToLine

        if ('START' in splitLine):
            outfile.write(line.rstrip() +'\n')                

        elif ('END' in splitLine):
            outfile.write(line.rstrip() +'\n')
        else:
            outfile.write(line.rstrip() + activity_data[activity_instance_id] +'\n')

    # close files
    f.close()
    outfile.close()

    return number_simulated_activities, ordered_file_path

if __name__ == "__main__":

    rule_file_name = sys.argv[1]

    if sys.platform == "darwin":
        rule_file_path = "examples/" + rule_file_name
    else:
        rule_file_path = "examples\\" + rule_file_name

    if sys.platform == "darwin":
        output_path = "output/"
    else:
        output_path = "output\\" 
    
    simulator_file_name = sys.argv[2]

    all_experiments_summary = ""


    #for target_number_activities in [50, 100, 500, 1000, 5000, 10000]:
    base = 1000

    for target_number_activities in [base, base*1.5, base*2, base*10]: #, base*10, base*20, base*50, base*100]:

        target_number_activities = int(target_number_activities)

        for number_data_elements in [2]:

            create_new_file = True

            if create_new_file:

                # create new event stream from parameters
                number_simulated_activities, ordered_simulated_file_path = create_eventstream_from_simulator(simulator_file_name, target_number_activities, number_data_elements)

                eventstream_file_path = ordered_simulated_file_path
                print("generated:"+eventstream_file_path)
            else:
                eventstream_file_path = sys.argv[2]
                number_simulated_activities = sum(1 for line in open(eventstream_file_path))

            
            m = Monitor("MyMonitor", rule_file_path)

            average = 0
            number_of_runs = 5
            throughput_average = 0

            for i in range(number_of_runs):
                assignment_vector, output_string, time_to_monitor = m.monitoringLoop(eventstream_file_path)
                m.reset()
                print("Trial "+str(i)+": "+str(round(time_to_monitor,4))+" seconds, "+"throughput: "+str(round(number_simulated_activities/time_to_monitor,4))+" activites / second")
                print(output_string)
                average += time_to_monitor
                throughput_average += (number_simulated_activities/time_to_monitor)

            experiment_summary = "\nExperiment Summary\n"
            experiment_summary += "rule:" + rule_file_path + "\n"
            experiment_summary += "event_stream:" + eventstream_file_path+"\n"
            experiment_summary += "length:"+str(number_simulated_activities)+"\n"
            experiment_summary += "Average compu time:" + str(average/number_of_runs)+"\n"
            experiment_summary += "Average throughput:"+ str(throughput_average/number_of_runs)+"\n"
            experiment_summary += "Overlap:"+ str(calculate_concurrency(eventstream_file_path))+"\n"

            print(experiment_summary)

            all_experiments_summary += experiment_summary

    print("\nAll Experiments Summary")
    print(all_experiments_summary)


