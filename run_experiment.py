# Raghubir Chimni and Isaac Mackey
# file created: 1/27/2021
# run_experiment.py
# main loop for initiating rule monitoring experiments

from datetime import datetime, timedelta
from simulation_manager import SimulationManager
from model_builder import ModelBuilder
from RuleMonitor.monitor import Monitor
import RuleMonitor.parser
from RuleMonitor.parser import generate_random_rule_with_fixed_process_atoms
import sys
import random
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import math

def calculate_moving_average(list_of_values, window_size):

    i = 0

    moving_averages = []

    while i < len(list_of_values) - window_size + 1:

        this_window = list_of_values[i : i + window_size]

        window_average = sum(this_window) / window_size

        moving_averages.append(window_average)

        i += 1

    for _ in range(window_size-1):
        moving_averages.append(window_average)

    return moving_averages

def remove_unfinished_processes(eventstream_file_path, new_eventstream_file_path):
    unfinished_process_instances = []

    with open(eventstream_file_path, 'r') as f:
        for d in f.readlines():
            d = d.strip()
            d_list = d.split(' ')

            if d_list[3]=="START":
                unfinished_process_instances.append(d_list[1])
            if d_list[3]=="END":
                if d_list[1] in unfinished_process_instances:
                    unfinished_process_instances.remove(d_list[1])
                else:
                    unfinished_process_instances.append(d_list[1])

    f.close()

    print(unfinished_process_instances)

    with open(new_eventstream_file_path, 'w') as outfile:
        with open(eventstream_file_path, 'r') as f:
            for d in f.readlines():
                d = d.strip()
                d_list = d.split(' ')
                if not d_list[1] in unfinished_process_instances:
                    outfile.write(d+'\n')   
        f.close()  
    outfile.close()

    return

def merge_eventstreams_consecutive(list_of_eventstream_file_paths, outfile_name):
    
    outfile = open(outfile_name, "w")

    log_sequence_number = 1
    process_instance_id_count = 1

    process_id_offset = 0

    for filename in list_of_eventstream_file_paths:

        max_process_instance_id = 1

        f = open(filename,'r')

        for line in f.readlines():
                
            splitLine = line.split()

            # new log sequence number
            splitLine[0] = str(log_sequence_number)
            log_sequence_number += 1

            # new process instance id
            if 'START' in splitLine:
                max_process_instance_id = max(max_process_instance_id, int(splitLine[1]))

            splitLine[1] = str(int(splitLine[1])+process_id_offset)

            newline = ' '.join(splitLine)

            outfile.write(newline+'\n')                

        process_id_offset += max_process_instance_id+1

        # close files
        f.close()
    outfile.close()

    remove_unfinished_processes(outfile)

# calculate number of atoms used in a monitor across all of its rules list
def calculate_activity_atoms_per_monitor(rule_monitors):
    number_of_body_atoms = []
    number_of_head_atoms = []

    for rule_monitor in rule_monitors:
        number_of_body_atoms.append(len(rule_monitor.ruleVector[0].bodyProcessAtoms))
        number_of_head_atoms.append(len(rule_monitor.ruleVector[0].headProcessAtoms))

    return number_of_body_atoms, number_of_head_atoms

# INPUT: filename for an eventstream
# OUTPUT: concurrency in the eventstream, i.e. on average, how many process instances are active when an activity starts
def calculate_concurrency(filename):

    f = open(filename,'r')

    # calculate concurrency
    unfinished_activites = 0
    count_activities = 0
    total_overlaps = 0
    concurrency_list = []
    for line in f.readlines():
        if('START' in line):
            count_activities += 1
            total_overlaps += unfinished_activites
            unfinished_activites += 1
        elif('END' in line):
            unfinished_activites -= 1
        concurrency_list.append(unfinished_activites)
    
    average_concurrency = total_overlaps/count_activities

    f.close()
    return average_concurrency, concurrency_list

def calculate_average_activities_per_process_instance(filename):

    f = open(filename, 'r')

    highest_process_instance_id = 1
    number_activities = 0

    for line in f.readlines():
        highest_process_instance_id = max(int(line.split()[1]), highest_process_instance_id)
        if not 'START' in line and not 'END' in line:
            number_activities += 1

    return number_activities/highest_process_instance_id

def create_eventstream_from_simulator(simulator_file_name, number_activities, limit):
    
    # simulator generates ~950 activities per day
    simulated_days = (1.25*number_activities/950)

    sm = SimulationManager(start = datetime.datetime.now(), end = datetime.datetime.now() + timedelta(days=simulated_days))

    simulator_file_name = simulator_file_name + "_" +str(number_activities)+'act'

    # different resource_limit values produce different amounts of overlap between process instances
    # limits = 5    => overlap ~40+
    # limits = 10   => overlap ~20
    # limits = 50   => overlap ~10

    # writes results into <filename>.txt
    sm.simulate(name=simulator_file_name,resource_limit={'support': limit, 'trust': limit}) 

    # Get file path for output of simulation
    # Use sys.platform to distinguish between Mac OS / Windows
    if sys.platform == "darwin":
        simulator_output_path = "output/" + simulator_file_name + '.txt'
    else:
        simulator_output_path = "output\\" + simulator_file_name + '.txt'

    #Opens file to read simulator output
    f = open(simulator_output_path)

    number_simulated_activities = sum(1 for line in open(simulator_output_path))

    average_overlap = calculate_concurrency(simulator_output_path)
    print("average_overlap in simulation:",str(average_overlap))

    cleaned_file_path = ""

    # Open file to write ordered output into
    if sys.platform == "darwin":
        cleaned_file_path = "output/" + simulator_file_name + "_cleaned.txt"
    else:
        cleaned_file_path = "output\\" + simulator_file_name + "_cleaned.txt"

    outfile = open(cleaned_file_path, "w")

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

    number_activities_in_output = 0

    for line in f.readlines():
        
        if number_activities_in_output < number_activities:
            number_activities_in_output += 1
        else:
            break
        
        line = line[:line.index("#")-1] # remove '#' and everything beyond
        splitLine = line.split()

        activity_instance_id = splitLine[1]

        if activity_instance_id not in activity_data.keys():            
            activity_data[activity_instance_id] = ' Name=' + random.choice(data_element_lists[0])

        if ('START' in splitLine):
            outfile.write(line.rstrip() +'\n')                

        elif ('END' in splitLine):
            outfile.write(line.rstrip() +'\n')
        else:
            outfile.write(line.rstrip() + activity_data[activity_instance_id] +'\n')

    # close files
    f.close()
    outfile.close()

    return number_activities_in_output, cleaned_file_path

# Input:    monitor file, log file, batch size, number of runs (take average)
# Output:   processing time for each batch, assignment/violation vector 
def run_trial(rule_monitor, eventstream_file_path, batch_size, number_of_runs):

    # average time to process batch of events over multiple runs of the same monitor
    average_batch_processing_times = []

    # number of times to run experiment to average over noisy data
    for i in range(number_of_runs):

        # initiate the monitoring loop on the Monitor class
        assignment_vector, output_string, time_to_monitor, event_processing_times = rule_monitor.monitoring_loop( eventstream_file_path, batch_size)
        rule_monitor.reset()
        
        print("len(event_processing_times): ",str(len(event_processing_times)))

        print("Trial "+str(i)+": "+str(round(time_to_monitor,4))+" seconds")
        print(output_string)
        
        # we want to measure the steady-state performance
        # remove the initial event, which includes loading time
        event_processing_times.pop(0)
        #duplicate the last event to maintain round number length of log
        event_processing_times.append(event_processing_times[-1])
        
        batch_processing_times = []

        # sum the processing times for the events in each batch from all monitors
        for i in range(math.ceil(len(event_processing_times)/batch_size)):
            subtotal = 0
            if (i+1)*batch_size < len(event_processing_times):
                subtotal += sum(event_processing_times[i*batch_size:(i+1)*batch_size])
            else:
                subtotal += sum(event_processing_times[i*batch_size:])

            batch_processing_times.append(subtotal/batch_size)

        average_batch_processing_times.append(sum(batch_processing_times)/len(batch_processing_times))

    # list of processing time for each batch
    return average_batch_processing_times

if __name__ == "__main__":
    date_and_time = str(datetime.datetime.now())
    date_and_time = date_and_time.replace(':', '--')
        
    simulator_file_name = sys.argv[1]

    all_experiments_summary = ""

    # if True, a new eventstream will be created from LogGenerator simulator
    # if False, an existing eventstream will be used
    if True:
        # set target number of activites for log
        number_events = 1000
        resource_limit = 50

        # create new event stream from parameters
        number_events, eventstream_file_path = create_eventstream_from_simulator(simulator_file_name, number_events, resource_limit)

        print("generated log: "+eventstream_file_path)
    else:
        #eventstream_file_path = 'logs/overlap_10000act_eventstream.txt'
        eventstream_file_path = 'logs/short_test_log.txt'
        
        number_events = sum(1 for line in open(eventstream_file_path))

    # Experiment for process model length
    if False:
    
        # generate rule monitors
        rule_monitors = []
        number_of_monitors = 12

        for i in range(number_of_monitors):
            m = Monitor("monitor", "random")
            rule_monitors.append(m)
            
        rule_string = ""

        for r in rule_monitors:
            print(str(r.ruleVector[0]))
            rule_string += str(r.ruleVector[0])+"\n"

        batch_processing_times = run_batch_experiment(rule_monitors[0], eventstream_file_path, batch_sizes_for_trials)        

        average_activities_per_process_instance = calculate_average_activities_per_process_instance(eventstream_file_path)

        # set axes range
        plt.xlim(5, 8)
        plt.ylim(0, max(batch_processing_times)*1.1)

        # 2D Scatter Plot
        plt.scatter(batch_sizes_for_trials, batch_processing_times)
        
        plt.xlabel("Average Activities Per Process Instance")
        plt.ylabel("Average Processing Time for a Batch (sec)")
        title_string = "Effect of Average Activities Per Process Instance on Average Processing Time for a Batch\n"
        title_string += "Rule File: "+rule_string+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        plt.title(title_string, fontdict={'fontsize': 8})
        plt.tight_layout()
        plt.show()
        plt.clf() 

    # Experiment for batch size
    if False:

        # generate rule monitors
        rule_monitors = []
        number_of_monitors = 3

        for i in range(number_of_monitors):
            m = Monitor("monitor", "random")
            rule_monitors.append(m)
            
        rule_string = ""

        for r in rule_monitors:
            print(str(r.ruleVector[0]))
            rule_string += str(r.ruleVector[0])+"\n"

        batch_sizes_for_trials = [1,5,10,20]

        average_batch_processing_times = []

        # run a trial for each batch
        for batch_size in batch_sizes_for_trials:

            batch_processing_times = []

            for rule_monitor in rule_monitors:

                number_of_runs = 3

                list_of_times = run_trial(rule_monitor, eventstream_file_path, batch_size, number_of_runs)

                # append one number per monitor, the average time to process a batch
                batch_processing_times.append(sum(list_of_times)/len(list_of_times))

            average_batch_processing_times.append(sum(batch_processing_times)/len(batch_processing_times))

        # set axes range
        plt.xlim(0, max(batch_sizes_for_trials)+1)
        plt.ylim(0, max(average_batch_processing_times)*1.1)

        # 2D Scatter Plot
        plt.scatter(batch_sizes_for_trials, average_batch_processing_times)
        
        plt.xlabel("Batch Size")
        plt.ylabel("Average Processing Time for a Batch (sec)")
        title_string = "Effect of Batch Size on Average Processing Time for a Batch\n"
        title_string += "Rule File: "+rule_string+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        plt.title(title_string, fontdict={'fontsize': 8})
        plt.tight_layout()
        plt.show()
        plt.clf()  

    # Experiment for number of activity atoms in body and head
    if True:

        # generate rule monitors
        rule_monitors = []

        for x in range(2,5):
            for y in range(2,5):
                m = Monitor("monitor", "random")
                m.ruleVector = [generate_random_rule_with_fixed_process_atoms(x,y)]
                rule_monitors.append(m)
        
        number_of_body_atoms, number_of_head_atoms = calculate_activity_atoms_per_monitor(rule_monitors)

        # run trials
        batch_processing_times = []

        for i,rule_monitor in enumerate(rule_monitors):
            print("Monitor "+str(i))

            batch_size = 100

            number_of_runs = 5

            one_trial_batch_processing_times = run_trial(rule_monitor, eventstream_file_path, batch_size, number_of_runs)

            batch_processing_times.append(sum(one_trial_batch_processing_times)/len(one_trial_batch_processing_times))
        
        title_string = "Effect of Number of Activity Atoms in Body and Head on Batch Processing Time\n"
        # title_string += "Monitors File: "+list_of_monitors+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        '''
        # 3D Plot
        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection='3d')
        ax.scatter3D(number_of_body_atoms, number_of_head_atoms, batch_processing_times)
        ax.set_xlabel('Number of Body Atoms in Monitor', fontweight = 'bold')
        ax.set_ylabel('Number of Head Atoms in Monitor', fontweight = 'bold')
        ax.set_zlabel('Average Processing Time for Batch of Size '+str(batch_size)+' (sec)', fontweight = 'bold')
        plt.title(title_string)
        plt.tight_layout()
        plt.show()
        plt.clf()
        '''

        # Table
        val1 = range(1,max(number_of_head_atoms)+1)
        val2 = range(1,max(number_of_body_atoms)+1)
        val3 = [["" for _ in range(len(val1))] for _ in range(len(val2))]

        for i in range(len(batch_processing_times)):
            print(number_of_body_atoms[i])
            print(number_of_head_atoms[i])
            val3[number_of_body_atoms[i]-1][number_of_head_atoms[i]-1] = format(batch_processing_times[i], '.5f')
   
        fig, ax = plt.subplots() 

        header = ax.table(cellText=[['']],
                      colLabels=['Number of Head Atoms'],
                        bbox=[0,.35, 1,.5]
                      )
        
        rowTitle = ax.table(cellText=[['']],
                      rowLabels=['Number  \nof  \nBody  \nAtoms  '],
                        bbox=[-.0079,0, .2,.6] #x,y,w,h
                      )
        ax.set_axis_off() 
        
        table = ax.table( 
            cellText = val3,
            rowLabels = val2,   
            colLabels = val1, 
            cellLoc ='center',  
            bbox=[0, 0, 1.2, .6],
            
            )         

        ax.set_title(title_string, 
             fontweight ="bold") 
        
        if sys.platform == "darwin":
            table_output_path = "plots/" + date_and_time + '.png'
        else:
            table_output_path = "plots\\" + date_and_time + '.png'

        plt.savefig(table_output_path, bbox_inches="tight", pad_inches=1)
        plt.show() 
        plt.clf()

'''
    # Experiment for number of rules
    if False:
        number_of_runs = 1

        number_of_rules = []
        batch_processing_times = []

        for i,rule_monitor in enumerate(rule_monitors):
            print("Monitor "+str(i))
            for m in rule_monitor:
                print(m.ruleFile)
            number_of_rules.append(len(rule_monitor))

            batch_size = 100

            one_trial_batch_processing_times = run_trial(rule_monitor, eventstream_file_path, batch_size, number_of_runs)

            batch_processing_times.append(sum(one_trial_batch_processing_times)/len(one_trial_batch_processing_times))
        
        # set axes range
        plt.xlim(0, max(number_of_rules)+1)
        plt.ylim(0, max(batch_processing_times)*1.1)

        # 2D Scatter Plot
        plt.scatter(number_of_rules, batch_processing_times)
        xint = range(1, math.ceil(max(number_of_rules))+1)
        plt.xticks(xint)
        plt.xlabel("Number of Rules in Monitor")
        plt.ylabel('Processing Time for Batch of Size '+str(batch_size)+" (sec)")
        title_string = "Effect of Number of Rules on Batch Processing Time\n"
        title_string += "Monitors File: "+list_of_monitors+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        plt.title(title_string)
        plt.tight_layout()
        plt.show()
        plt.clf()

    # Experiment for number of rules and number of activity atoms
    if False:
        number_of_rules = [len(x) for x in rule_monitors]
        number_of_activity_atoms = calculate_activity_atoms_per_monitor(rule_monitors)                

        batch_processing_times = []

        for i,rule_monitor in enumerate(rule_monitors):
            print("Monitor "+str(i))
            for m in rule_monitor:
                print(m.ruleFile)

            batch_size = 100

            one_trial_batch_processing_times = run_trial(rule_monitor, eventstream_file_path, batch_size, number_of_runs)

            batch_processing_times.append(sum(one_trial_batch_processing_times)/len(one_trial_batch_processing_times))

        # 3D Plot
        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection='3d')
        ax.scatter3D(number_of_rules, number_of_activity_atoms, batch_processing_times)
        ax.set_xlabel('Number of Rules in Monitor', fontweight = 'bold')
        ax.set_ylabel('Number of Activity Atoms Being Monitored', fontweight = 'bold')
        ax.set_zlabel('Processing Time for Batch of Size '+str(batch_size)+' (sec)', fontweight = 'bold')
        title_string = 'Effect of Number of Rules and Activity Atoms on Processing Time'
        title_string += "Rule File: "+list_of_monitors+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        
        fig.tight_layout()
        plt.title(title_string)
        plt.show()
        plt.clf()

    # Experiment for number of concurrent activities
    if False:

        average_overlap, overlap_list = calculate_concurrency(eventstream_file_path)

        batch_size = 20
        batch_processing_times = run_trial(rule_monitors[0], eventstream_file_path, batch_size, 1)

        # smooth with moving average
        window_size = 1000
        smooth_overlap_list = calculate_moving_average(overlap_list, window_size)
        batch_processing_times = calculate_moving_average(batch_processing_times, 100)

        #smaller_length = min(len(smooth_overlap_list),len(smooth_batch_processing_times))

        #smooth_overlap_list = smooth_overlap_list[:smaller_length]
        #smooth_batch_processing_times = smooth_batch_processing_times[:smaller_length]

        xlabels_for_overlap = range(len(smooth_overlap_list))

        xlabels_for_processing_times = [i*batch_size for i in range(len(batch_processing_times))]

        fig, ax1 = plt.subplots()

        # 2D Plot with Two Data Sets with Different Axes
        color = 'tab:red'

        ax1.set_xlabel('Log Sequence Number (#)')
        ax1.set_ylabel('Number of Concurrent Process Instances (#)', color=color)
        ax1.plot(xlabels_for_overlap, smooth_overlap_list, color=color)
        ax1.tick_params(axis='y', labelcolor = color)

        ax2 = ax1.twinx()

        color = 'tab:blue'
        ax2.set_ylabel('Processing Time (s)')
        ax2.plot(xlabels_for_processing_times, batch_processing_times, color=color)
        # set y-range
        ax2.tick_params(axis='y',labelcolor=color)
   
        title_string = "Effect of Concurrent Process Instances on Batch Processing Time\n"
        title_string += "Rule File: "+rule_string+"\n"
        title_string += "Eventstream File: "+eventstream_file_path
        
        fig.tight_layout()
        plt.title(title_string)
        plt.show()

        plt.show()
        plt.clf()

    # only add to log if an experiment was run
    if title_string:
        if sys.platform == "darwin":
            data_output_path = "data/" + date_and_time + '.txt'
        else:
            data_output_path = "data\\" + date_and_time + '.txt'
        
        with open(data_output_path, 'w') as outfile:
            outfile.write(title_string+'\n')   
            outfile.write(date_and_time+'\n')
            for t in batch_processing_times:
                outfile.write(str(t)+'\n')
        outfile.close()
'''

'''
    for x,y in zip(indexes,actTimes):
        label = "{:.4f}".format(y)
        plt.annotate(label, (x,y), textcoords="offset points", xytext=(3,2),ha='center',rotation=45)
'''

