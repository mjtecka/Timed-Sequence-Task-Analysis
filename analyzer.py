### Analyzer / operant box - mice experiments [Krabimyše]
# 
#
#   Code: Milan Janíček <mjtecka@gmail.com>
#   
#   input - data by tasks - from ./data/data_by_task/
#   output - csv for experiments - into ./data/subanalysis_results/*
#
#   runs specified analyses and outputs data into specified directory
#   data_loader is needed for loading the data (groups and mice ids are in data_loader script
#   
###


import data_loader
import json
import csv
import os

from statistics import median, mean


#--configuration--

#predefined tasks list - defines which data should be analysed
tasks_list = [
        'Extinction',
        'LLPP-0.5_5-0.5_20-1.5_5',
        'LLPP-alternating',
        'Re-baseline',
    #    'Habituation-3',
        'LLPP-0.5_5-0.5_20',
        'LLPP',
        'LLP',		
        'LLPP-0.5_5-3_20-0.5_5',
        'LP',
        'LLPP-0.5_2-0.5_10',
        'LLPP-1.5_5-0.5_20-0.5_5',
    #    'Operant-training'
        ]

#task = "Extinction"
#task = "LLPP"
#task = "LLPP-0.5_5-0.5_20"

#mice_order is used from data_loader
mice_order = data_loader.mice_order


#defines correct, incorrect and in_timeout presses (in regard to operant box codes)
correct_presses=["1","101","102","103","104"]
incorrect_presses=["65","66","67","75","76","77","78","79"]
in_timeout_presses=["68","69"]
#defines last timestamp (= timeout)
last_timestamp = 360000


#/--- tools --

#simple counter of specific codes
#counts occurences of specific codes - single code can be selected as single value in array
def results_number_presses(response_codes, dataset):

    results={}
    for mid in dataset.keys():
        results[mid]={}
        for d in sorted(dataset[mid].keys()):
#            print ("COUNTER number_presses: mouse:"+mid+", day:"+str(d))
            code_count=0
            result_set =  dataset[mid][d]["data"]

            for timestamp in sorted(result_set.keys()):
                #works with array of codes too now...
                for response_code in response_codes:
                    #eg response code = 200
                    if response_code in result_set[timestamp] :
                        code_count += 1

            results[mid][d]=code_count

    #print(json.dumps(results))

    return results

#counts code sequences in each trial - specifically it shows how trial failed (correct trials are always the same) 
def get_sequences_per_trial(dataset):

    sequences = {}
    for mid in dataset.keys():
        sequences[mid]={}
        for d in sorted(dataset[mid].keys()):
            #identify trials
            trial=0
            trial_start_timestamp = 0
            sequences[mid][d] = {}
            sequence = ""
            result_set = dataset[mid][d]["data"]

            # for each trial, put sequences for timestamp (first timestamp of sequence)
            for timestamp in sorted(result_set.keys()):
                #trial_start_timestamp =0 means we should use current timestamp and init dict
                if trial_start_timestamp == 0:
                    sequences[mid][d][trial] = {}
                    trial_start_timestamp = timestamp
                for code in sorted(result_set[timestamp]):
                    #check correct - if correct, add to sequence
                    if code in correct_presses:
                        sequence = sequence+"->"+code

                    #check incorrect - if incorrect, add to sequence, store sequence, change trial, trial_start_timestamp
                    if code in incorrect_presses + in_timeout_presses:
                        sequence = sequence+"->"+code
#                        print("S-incorrect:" + sequence)
                        sequences[mid][d][trial][timestamp] = sequence
                        sequence = ""
                    #check reinforcement or timeout - change trial as well
                    if code in ["2","3"] :
                        sequence = sequence+"->"+code
#                        print("S-reinf:" + sequence)
                        sequences[mid][d][trial][timestamp] = sequence
                        trial +=1
                        trial_start_timestamp = 0
                        sequence = ""

    return sequences

#counts specific sequences by day, not trial
def count_sequences_by_day(sequences):

    results = {}
    for mid in sequences.keys():
        results[mid] ={}
        for d in sorted(sequences[mid].keys()):
            results[mid][d] = {}
            day_sequences = sequences[mid][d]
            for t in day_sequences.keys():
                for ts in day_sequences[t]:
                    try:
                        s = day_sequences[t][ts]
                        results[mid][d][s] += 1
                    except KeyError:
                        results[mid][d][s] = 1

    return results

#----- subanalyses definitions ----

#analyze sequences - look for singals (codes in mydataset) and put them into "buckets" by time interval
def analyze_response_codes_per_interval(task, response_codes,interval=6000):

    print("analyze: presses per interval "+str(interval))
    subanalysis_name="presses-per-interval-"+str(interval) 

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv" 

    #go through dataset timestamps, count presses, add to given range in results (=bucket) accordingly
    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results[mid][d]={}
            result_set = my_dataset[mid][d]["data"]
            #create bucket range, for each timestamp count reposonse codes and add to according buckets            

            # generate zero values for given range in results
            i = 0
            ts = 0
            while ts < last_timestamp :
                ts = ts+interval
                results[mid][d][i]=0
                i +=1

            #check response code on each timestamp, if response code is detected, increment bucket timestamp % interval
            for timestamp in sorted(result_set.keys()):
                #works with array of codes too now...
                for response_code in response_codes:
                    #eg response code = 200
                    if response_code in result_set[timestamp] :
                        which_bucket = timestamp // interval
#                        print ("timestamp: " + str(timestamp) + " interval: "+str(interval)+ " which_bucket: " + str(which_bucket))
                        try:
                            results[mid][d][which_bucket] += 1
                        except KeyError:
                            results[mid][d][which_bucket] = 1

    print(json.dumps(results,indent=4)) 

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
   
        csvwriter.writerow(["#Count response codes per interval["+str(interval)])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","bucket","code count"])
        csvwriter.writerow(["mid", "grp","day","date","bucket","code_count"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #bucket
                    for b in results[m][d].keys():
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], b, results[m][d][b]])


#analyze sequences - look for singals (codes in mydataset) and put them into "buckets" by interval INCREMENT TOTAL COUNT
#usage analyze_response_codes_per_interval_incremental(task, correct_presses, "correct") 
#task_name is used for naming files (eg. incorrect, correct,) and should be used based on response_codes array
def analyze_response_codes_per_interval_incremental(task, response_codes, task_name="default", interval=6000):


    print("analyze: presses per interval -incremental- "+str(interval))
    subanalysis_name=task_name+"-codes-per-interval-incremental"+str(interval) 

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv"

    #go through dataset timestamps, count presses, add to right bucket
    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results[mid][d]={}
            result_set = my_dataset[mid][d]["data"]
            #create bucket range, for each timestamp count reposonse codes and add to according buckets            
                #check response code on each timestamp, if response code is detected, increment bucket timestamp % interval

            # generate zero values for given range in results
            i = 0
            ts = 0
            while ts < last_timestamp :
                ts = ts+interval
                results[mid][d][i]=0
                i +=1

            which_bucket=0
            #next_time_marker - on which timestamp we should change bucket
            next_time_marker=interval
            overall_count=0
            #go through timestamps, increment bucket when interval is reached
            for timestamp in sorted(result_set.keys()):
                #if timestamp is over next_time_marker, increment bucket and update next_time_marker
                if timestamp > next_time_marker:
                    which_bucket +=1
                    next_time_marker = next_time_marker + interval

                #works with array of codes too now...
                for response_code in response_codes:
                    #eg response code = 200
                    if response_code in result_set[timestamp] :
                        overall_count += 1 
                        #which_bucket = timestamp // interval
                        print ("mid: "+mid+" d:"+str(d)+ " timestamp: " + str(timestamp) + " response_code: "+ response_code + " which_bucket: " + str(which_bucket))
                        try:
                            results[mid][d][which_bucket] = overall_count #NOTE - differs here
                        except KeyError:
                            results[mid][d][which_bucket] = 1

            #normalize iteration (add something to all buckets)
#            print("normalization")
            n = 0
            final_bucket = last_timestamp // interval
#           print(final_bucket)
            for b in range(0,final_bucket):
                if results[mid][d][b] !=0:
                    n = results[mid][d][b]
                # put n in buckets containing 0
                elif results[mid][d][b] == 0:
                    results[mid][d][b] = n


    print(json.dumps(results,indent=4)) 

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
   
        csvwriter.writerow(["#Count response codes per interval ["+str(interval)+"] , INCREMENTAL, "+task_name])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","bucket","code count"])
        csvwriter.writerow(["mid", "grp","day","date","bucket","code_count"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #bucket
                    for b in results[m][d].keys():
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], b, results[m][d][b]])




#analyze sequences - look for singals (codes in mydataset) and put them into "buckets" by trial
def analyze_response_codes_per_trial(task, response_codes):

    print("analyze: presses per trial")
    subanalysis_name="presses-per-trial"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv" 

    #go through dataset timestamps, count presses, add to right bucket
    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results[mid][d]={}
            result_set = my_dataset[mid][d]["data"]
            #create bucket range, for each timestamp count reposonse codes and add to according buckets            
                #check response code on each timestamp, if response code is detected, increment bucket timestamp % interval

            which_bucket=0
            for timestamp in sorted(result_set.keys()):
                #works with array of codes too now...
                for response_code in response_codes:
                    #eg response code = 200
                    if response_code in result_set[timestamp] :
                        print ("mid: "+mid+" d:"+str(d)+ " timestamp: " + str(timestamp) + " response_code: "+ response_code + " which_bucket: " + str(which_bucket))
                        try:
                            results[mid][d][which_bucket] += 1
                        except KeyError:
                            results[mid][d][which_bucket] = 1
                #increment which_bucket when reinforcement detected (final correct press is in same timestamp, press should be counted first)
                if "2" in result_set[timestamp]:
                    which_bucket +=1
                    

    print(json.dumps(results,indent=4))

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Count response codes per trial"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","bucket","code count"])
        csvwriter.writerow(["mid", "grp","day","date","bucket","code_count"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #bucket
                    for b in results[m][d].keys():
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], b, results[m][d][b]])


#analyze trial times  and put them into "buckets" 
def analyze_trial_times(task):

    print("analyze: time per trial")
    subanalysis_name="time-per-trial"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/"
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv" 


    #go through dataset timestamps, look for trials, add to buckets
    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results[mid][d]={}
            result_set = my_dataset[mid][d]["data"]
            which_bucket=0
            #trial_start_timestamp when previous trial started?
            trial_start_timestamp = 0 

            for timestamp in sorted(result_set.keys()):
                #works with array of codes too now...
                    
                if "2" in result_set[timestamp] :
                   #write into bucket, increment bucket, change trial_stamp_timestamp
                   print ("mid: "+mid+" d:"+str(d)+ " timestamp: " + str(timestamp) + " trial_start_timestamp "+ str(trial_start_timestamp) + " which_bucket: " + str(which_bucket))
                   results[mid][d][which_bucket] = timestamp - trial_start_timestamp
                   which_bucket += 1 
                   trial_start_timestamp = timestamp
 
    print(json.dumps(results,indent=4))

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Time per trial"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","bucket","time (ms)"])
        csvwriter.writerow(["mid", "grp","day","date","bucket","time"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #bucket
                    for b in results[m][d].keys():
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], b, results[m][d][b]])


#session duration (time to complete 40 trials)
def analyze_trial_time(task):
#input_file = './data/original_data/data_vpa_final.csv'
    print("analyze: session duration (time to complete 40 trials)")
    subanalysis_name="session_time" 

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path)
    
    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_session_time= output_path+task+'-'+subanalysis_name+".csv" 

    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            result_set = my_dataset[mid][d]["data"]
            keys = sorted(result_set.keys())
#            print("last timestamp" + str(keys[-1]))
            #get last timestamp from all timestamps
            results[mid][d] = keys[-1]

    #output
    with open(output_session_time, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
    
        csvwriter.writerow(["#Session times"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","last recorded timestamp","human readable time"])
        csvwriter.writerow(["mid", "grp","day","date","time_10ms","time_min"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"],results[m][d],data_loader.get_timestamp(results[m][d])])


#number of successfully completed trials (rewards)
def count_completed_trials(task):
    print("analyze: number of successfully completed trials (rewards)")
    subanalysis_name="count_completed" 

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    count_completed= output_path+task+'-'+subanalysis_name+".csv" 
    #count_completed='./data/analysis_results/'+task+'-count_completed.csv'

    results={}

    results = results_number_presses(["2"], my_dataset)

    with open(count_completed, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Reinforcement issued"])
        csvwriter.writerow(["#mouse id", "group", "day","number of issued reinforcements (0.2)"])
        csvwriter.writerow(["mid", "grp","day","correct"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    csvwriter.writerow([m,g,d,results[m][d]])

#number of ALL presses in trial
#normalized presses - presses /per reinforcement
def count_all_presses(task):
    print("analyze : number of ALL presses in trial")
    subanalysis_name="count_all_presses" 
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    #count_presses='./data/analysis_results/'+task+'-count_presses.csv'
    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    count_presses = output_path+task+'-'+subanalysis_name+".csv"

    results={}

    #presses
    #note - first record is 0.5, 0.51 - counting 0.5 is +1 compared to array of error codes, better to use specific codes (.6x,.7x)
    results = results_number_presses(incorrect_presses+correct_presses+in_timeout_presses,my_dataset)
    #count reinforcement issued (to be able to normalize)
    results_reinf = results_number_presses(["2"], my_dataset)

    with open(count_presses, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Incorrect and correct presses count"])
        csvwriter.writerow(["#mouse id", "group", "day","number of all presses (0.1,0.5)","presses normalized per reinforecement"])
        csvwriter.writerow(["mid", "grp","day","all_presses","normalized_all_presses"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #presses per reinforcement?
                    per_reinforcement=None
                    try :
                        per_reinforcement= results[m][d] / results_reinf[m][d]
                    except ZeroDivisionError:
                        per_reinforcement="-"

                    #print("working on- m:"+str(m)+" d:"+str(d)+" results[m][d]:"+str(results[m][d]))  
                    csvwriter.writerow([m,g,d,results[m][d],per_reinforcement])


#number of CORRECT presses in trial
#normalized presses - presses /per reinforcement
def count_correct_presses(task):
    print("analyze : number of CORRECT presses in trial")
    subanalysis_name="count_correct_presses"
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    #count_presses='./data/analysis_results/'+task+'-count_presses.csv'
    output_path="./data/subanalysis_results/"+subanalysis_name+"/"
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    count_presses = output_path+task+'-'+subanalysis_name+".csv" 

    results={}

    #presses
    results = results_number_presses(correct_presses,my_dataset)
    #count reinforcement issued (to be able to normalize)
    results_reinf = results_number_presses(["2"], my_dataset)

    with open(count_presses, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Correct presses count"])
        csvwriter.writerow(["#mouse id", "group", "day","number of correct presses (0.1)","presses normalized per reinforecement"])
        csvwriter.writerow(["mid", "grp","day","correct_presses","normalized_correct__presses"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #presses per reinforcement?
                    per_reinforcement=None
                    try :
                        per_reinforcement= results[m][d] / results_reinf[m][d]
                    except ZeroDivisionError:
                        per_reinforcement="-"

                    #print("working on- m:"+str(m)+" d:"+str(d)+" results[m][d]:"+str(results[m][d]))  
                    csvwriter.writerow([m,g,d,results[m][d],per_reinforcement])

#number of INCORRECT presses in trial
#normalized presses - presses /per reinforcement
# 68, 69 (timeout presses) dont count
def count_incorrect_presses(task):
    print("analyze : number of INCORRECT presses in trial")
    subanalysis_name="count_incorrect_presses" 
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    #count_presses='./data/analysis_results/'+task+'-count_presses.csv'
    output_path="./data/subanalysis_results/"+subanalysis_name+"/"
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    count_presses = output_path+task+'-'+subanalysis_name+".csv"

    results={}

    #presses
    #note - first record is 0.5, 0.51 - counting 0.5 is +1 compared to array of error codes
    results = results_number_presses(incorrect_presses,my_dataset)
    #count reinforcement issued (to be able to normalize)
    results_reinf = results_number_presses(["2"], my_dataset)

    #count all incorrect presses
    #    \   .65/.50     = Incorrect Right
    results_65=results_number_presses(["65"], my_dataset)
    #\   .66/.50     = Incorrect Left (low time)
    results_66=results_number_presses(["66"], my_dataset)
    #\   .67/.50     = Incorrect Left (high time) \\ it was incorrectly "Incorrect Right"
    results_67=results_number_presses(["67"], my_dataset)
#    #\   .68/.50     = Incorrect - Press Left during timeout
#    results_68=results_number_presses(["68"], my_dataset)
#    #\   .69/.50     = Incorrect - Press Right during timeout
#    results_69=results_number_presses(["69"], my_dataset)
    #\   .75/.50    = Incorrect Left
    results_75=results_number_presses(["75"], my_dataset)
    #\   .76/.50     = Incorrect 1st Right (low time)
    results_76=results_number_presses(["76"], my_dataset)
    #\   .77/.50     = Incorrect 1st Right (high time)
    results_77=results_number_presses(["77"], my_dataset)
    #\   .78/.50     = Incorrect 2nd Right (low time)
    results_78=results_number_presses(["78"], my_dataset)
    #\   .79/.50     = Incorrect 2nd Right (high time)
    results_79=results_number_presses(["79"], my_dataset)

    with open(count_presses, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Incorrect presses count"])
        csvwriter.writerow(["#mouse id",
                            "group",
                            "day",
                            "number of incorrect presses (0.1)",
                            "presses normalized per reinforecement",
                            "incorrect right (0.65)",
                            "incorrect left (0.66)",
                            "incorrect left high time (0.67)",
#                            "incorrect left - left during timeout (0.68)",
#                            "incorrect right - right during timeout (0.69)",
                            "incorrect left (0.75)",
                            "incorrect 1st right - low time (0.76)",
                            "incorrect 1st right - high time (0.77)",
                            "incorrect 2nd right - low time (0.78)",
                            "incorrect 2nd right - high time (0.79)"
                            ])
        csvwriter.writerow(["mid",
                            "grp",
                            "day",
                            "incorrect_presses",
                            "normalized_incorrect_presses",
                            "incorrect_65",
                            "incorrect_66",
                            "incorrect_67",
#                            "incorrect_68",
#                            "incorrect_69",
                            "incorrect_75",
                            "incorrect_76",
                            "incorrect_77",
                            "incorrect_78",
                            "incorrect_79"
                            ])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #presses per reinforcement?
                    per_reinforcement=None
                    try :
                        per_reinforcement= results[m][d] / results_reinf[m][d]
                    except ZeroDivisionError:
                        per_reinforcement="-"

                    #print("working on- m:"+str(m)+" d:"+str(d)+" results[m][d]:"+str(results[m][d]))  
                    csvwriter.writerow([m,
                                        g,
                                        d,
                                        results[m][d],
                                        per_reinforcement,
                                        results_65[m][d],
                                        results_66[m][d],
                                        results_67[m][d],
#                                        results_68[m][d],
#                                        results_69[m][d],
                                        results_75[m][d],
                                        results_76[m][d],
                                        results_77[m][d],
                                        results_78[m][d],
                                        results_79[m][d]                                                                
                                            ])

#number of IN TIMEOUT presses in trial
#normalized presses - presses /per reinforcement
# only 68, 69 (timeout presses) count
def count_in_timeout_presses(task):
    print("analyze : number of IN TIMEOUT presses in trial")
    subanalysis_name="count_in_timeout_presses"
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    #count_presses='./data/analysis_results/'+task+'-count_presses.csv'
    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    count_presses = output_path+task+'-'+subanalysis_name+".csv"

    results={}

    #presses
    #note - first record is 0.5, 0.51 - counting 0.5 is +1 compared to array of error codes
    results = results_number_presses(in_timeout_presses,my_dataset)
    #count reinforcement issued (to be able to normalize)
    results_reinf = results_number_presses(["2"], my_dataset)

    #count all incorrect presses
    #    \   .65/.50     = Incorrect Right
#    results_65=results_number_presses(["65"], my_dataset)
    #\   .66/.50     = Incorrect Left (low time)
#    results_66=results_number_presses(["66"], my_dataset)
    #\   .67/.50     = Incorrect Left (high time) \\ it was incorrectly "Incorrect Right"
#    results_67=results_number_presses(["67"], my_dataset)
    #\   .68/.50     = Incorrect - Press Left during timeout
    results_68=results_number_presses(["68"], my_dataset)
    #\   .69/.50     = Incorrect - Press Right during timeout
    results_69=results_number_presses(["69"], my_dataset)
    #\   .75/.50    = Incorrect Left
#    results_75=results_number_presses(["75"], my_dataset)
    #\   .76/.50     = Incorrect 1st Right (low time)
#    results_76=results_number_presses(["76"], my_dataset)
    #\   .77/.50     = Incorrect 1st Right (high time)
#    results_77=results_number_presses(["77"], my_dataset)
    #\   .78/.50     = Incorrect 2nd Right (low time)
#    results_78=results_number_presses(["78"], my_dataset)
    #\   .79/.50     = Incorrect 2nd Right (high time)
#    results_79=results_number_presses(["79"], my_dataset)

    with open(count_presses, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#In timeout presses count"])
        csvwriter.writerow(["#mouse id",
                            "group",
                            "day",
#                            "number of  presses (0.1)",
#                            "presses normalized per reinforecement",
#                            "incorrect right (0.65)",
#                            "incorrect left (0.66)",
#                            "incorrect left high time (0.67)",
                            "incorrect left - left during timeout (0.68)",
                            "incorrect right - right during timeout (0.69)"
#                            "incorrect left (0.75)",
#                            "incorrect 1st right - low time (0.76)",
#                            "incorrect 1st right - high time (0.77)",
#                            "incorrect 2nd right - low time (0.78)",
#                            "incorrect 2nd right - high time (0.79)"
                            ])
        csvwriter.writerow(["mid",
                            "grp",
                            "day",
#                            "in_timeout_presses",
#                            "normalized_in_timeout_presses",
#                            "incorrect_65",
#                            "incorrect_66",
#                            "incorrect_67",
                            "in_timeout_68",
                            "in_timeout_69"
#                            "incorrect_75",
#                            "incorrect_76",
#                            "incorrect_77",
#                            "incorrect_78",
#                            "incorrect_79"
                            ])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    #presses per reinforcement?
                    per_reinforcement=None
                    try :
                        per_reinforcement= results[m][d] / results_reinf[m][d]
                    except ZeroDivisionError:
                        per_reinforcement="-"

                    #print("working on- m:"+str(m)+" d:"+str(d)+" results[m][d]:"+str(results[m][d]))  
                    csvwriter.writerow([m,
                                        g,
                                        d,
#                                        results[m][d],
#                                        per_reinforcement,
#                                        results_65[m][d],
#                                        results_66[m][d],
#                                        results_67[m][d],
                                        results_68[m][d],
                                        results_69[m][d]
#                                        results_75[m][d],
#                                        results_76[m][d],
##                                        results_77[m][d],
#                                        results_78[m][d],
#                                        results_79[m][d]                                                                
                                            ])


#wrapper to get_sequences_per_trial - loads data for task, returns sequences in JSON
def test_sequences(task):
    print("test : sequences")
    subanalysis_name="test_sequences" 
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    sequences={}

    sequences = get_sequences_per_trial(my_dataset)
    print(json.dumps(sequences, indent=4)) 

    return sequences


#analyze sequences per day
def analyze_sequences(task):
    print("analyze : count sequences")
    subanalysis_name="count_sequences"
    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)
    #print(json.dumps(data_summary, indent=4))

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    count_sequences = output_path+task+'-'+subanalysis_name+".csv" 


    sequences = get_sequences_per_trial(my_dataset)
    seq_results = count_sequences_by_day(sequences)

    with open(count_sequences, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Count of sequences"])
        csvwriter.writerow(["#mouse id", "group", "day","sequence","sequence count"])
        csvwriter.writerow(["mid", "grp","day","sequence_string","sequence_count"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in seq_results[m].keys():
                    for s in seq_results[m][d].keys():
                        
                        #print("working on- m:"+str(m)+" d:"+str(d)+" results[m][d]:"+str(results[m][d]))  
                        csvwriter.writerow([m,g,d,s,seq_results[m][d][s]])



#analyze interval - 102->?->103
def analyze_interval_102_103(task):


    print("analyze: interval LL(?)P")
    subanalysis_name="interval-102-103"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/"
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv" 

    #go through dataset timestamps, look for trials, add to buckets
    intervals={}
    results={}
    for mid in my_dataset.keys():
        intervals[mid]={}
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            intervals[mid][d]={}
            results[mid][d]={}
            intervals[mid][d]["102-103"]=[]
            result_set = my_dataset[mid][d]["data"]
            interval_start_timestamp=0
            got_102 = False
            for timestamp in sorted(result_set.keys()):
                if "102" in result_set[timestamp] :
#                    print("got 102: timestamp: "+str(timestamp))
                    got_102 = True
                    interval_start_timestamp = timestamp
                    continue
                if got_102 and "103" in result_set[timestamp]:
#                    print("got 103 after 102: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals[mid][d]["102-103"].append(interval)
#                   print("writing interval: "+ str(interval))
                    got_102 = False
                elif got_102 and not "103" in result_set[timestamp]:
                    got_102 = False
#                   print("no 103 after 102: timestamp "+ str(timestamp))

            #count average per day
            for v in intervals[mid][d]["102-103"] :
                results[mid][d]["102-103"]={}
                results[mid][d]["102-103"]["avg"]= mean(intervals[mid][d]["102-103"])
                results[mid][d]["102-103"]["med"]= median(intervals[mid][d]["102-103"])

#            x = 0
#            for v in intervals[mid][d]["102-103"] :
#                x += v 
#            try:
#                results[mid][d]["102-103"] = x / len(intervals[mid][d]["102-103"])
#            except ZeroDivisionError:
#                results[mid][d]["102-103"] = "null"



#    print(json.dumps(intervals,indent=4))
#    print(json.dumps(results,indent=4))

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Mean interval LL(?)P - 102->103"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","average interval [s]","median interval [s]"])
        csvwriter.writerow(["mid", "grp","day","date","avg_interval-102-103","med_interval-102-103"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    try:
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], results[m][d]["102-103"]["avg"]/100, results[m][d]["102-103"]["med"]/100])
                    except KeyError:
                        continue



#analyze interval - 103->?->104
def analyze_interval_103_104(task):


    print("analyze: interval LLP(?)P")
    subanalysis_name="interval-103-104"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path):
        os.makedirs(output_path) 

    output_file= output_path+task+'-'+subanalysis_name+".csv" 

    #go through dataset timestamps, look for trials, add to buckets
    intervals={}
    results={}
    for mid in my_dataset.keys():
        intervals[mid]={}
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            intervals[mid][d]={}
            results[mid][d]={}
            intervals[mid][d]["103-104"]=[]
            result_set = my_dataset[mid][d]["data"]
            interval_start_timestamp=0
            got_103 = False
            for timestamp in sorted(result_set.keys()):
                if "103" in result_set[timestamp] :
#                    print("got 103: timestamp: "+str(timestamp))
                    got_103 = True
                    interval_start_timestamp = timestamp
                    continue
                if got_103 and "104" in result_set[timestamp]:
#                    print("got 104 after 103: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals[mid][d]["103-104"].append(interval)
#                   print("writing interval: "+ str(interval))
                    got_103 = False
                elif got_103 and not "104" in result_set[timestamp]:
                    got_103 = False
#                   print("no 104 after 103: timestamp "+ str(timestamp))

            #count average per day
            for v in intervals[mid][d]["103-104"] :
                results[mid][d]["103-104"]={}
                results[mid][d]["103-104"]["avg"]= mean(intervals[mid][d]["103-104"])
                results[mid][d]["103-104"]["med"]= median(intervals[mid][d]["103-104"])


#            x = 0
#            for v in intervals[mid][d]["103-104"] :
#                x += v 
#            try:
#                results[mid][d]["103-104"] = x / len(intervals[mid][d]["103-104"])
#            except ZeroDivisionError:
#                results[mid][d]["103-104"] = "null"



#    print(json.dumps(intervals,indent=4))
#    print(json.dumps(results,indent=4))

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Mean interval LLP(?)P - 103->104"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","average interval [s]","median interval[s]"])
        csvwriter.writerow(["mid", "grp","day","date","avg_interval-103-104","med_interval-103-104"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    try:
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], results[m][d]["103-104"]["avg"]/100,results[m][d]["103-104"]["med"]/100])
                    except KeyError:
                        continue

#analyze interval - 2->?
def analyze_interval_2_x(task):


    print("analyze: interval after reinforcment (2-x)")
    subanalysis_name="interval-2-x"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    output_file= output_path+task+'-'+subanalysis_name+".csv" 

    intervals={}
    results={}
    for mid in my_dataset.keys():
        intervals[mid]={}
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            intervals[mid][d]={}
            results[mid][d]={}
            intervals[mid][d]["2-x"]=[]
            result_set = my_dataset[mid][d]["data"]
            interval_start_timestamp=0
            got_102 = False
            for timestamp in sorted(result_set.keys()):
                if "2" in result_set[timestamp] :
#                    print("got 102: timestamp: "+str(timestamp))
                    got_102 = True
                    interval_start_timestamp = timestamp
                    continue
                if got_102 :
#                    print("got something(x) after 2: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals[mid][d]["2-x"].append(interval)
#                   print("writing interval: "+ str(interval))
                    got_102 = False
                #NOTE NOTE what about "3" after "2"?? NOTE

            #count average per day
            for v in intervals[mid][d]["2-x"] :
                results[mid][d]["2-x"]={}
                results[mid][d]["2-x"]["avg"]= mean(intervals[mid][d]["2-x"])
                results[mid][d]["2-x"]["med"]= median(intervals[mid][d]["2-x"])



#    print(json.dumps(intervals,indent=4))
#    print(json.dumps(results,indent=4))

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Mean interval after reinforcment - 2->x"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","average interval [s]", "median interval [s]"])
        csvwriter.writerow(["mid", "grp","day","date","avg_interval-2-x", "med_interval-2-x"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], results[m][d]["2-x"]["avg"]/100,results[m][d]["2-x"]["med"]/100])

#analyze intervals in correct sequence 101->?->102->?->103->?->104
#analyze timestamp in correct sequence 101->?->102->?->103->?->104
#note this anaylysis has 2 outputs!! - INTERVALS and TIMESTAMPS
def analyze_interval_correct_sequence(task):

    #INTERVALS
    print("analyze: intervals in correct sequence")
    subanalysis_name="intervals-correct_sequence"

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    output_file= output_path+task+'-'+subanalysis_name+".csv" 


    #TIMESTAMPS
    print("analyze (2): timestamps in correct sequence")
    subanalysis_name2="timestamps-correct_sequence"

    output_path2="./data/subanalysis_results/"+subanalysis_name2+"/"
    if not os.path.exists(output_path2):
        os.makedirs(output_path2) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file2= output_path2+task+'-'+subanalysis_name2+".csv" 


    #MAIN
    intervals={}
    timestamps={}
    results={}
    for mid in my_dataset.keys():
        intervals[mid]={}
        timestamps[mid]={}
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            intervals[mid][d]={}
            timestamps[mid][d]={}
            results[mid][d]={}
            intervals[mid][d]["101-102"]=[]
            intervals[mid][d]["102-103"]=[]
            intervals[mid][d]["103-104"]=[]

            result_set = my_dataset[mid][d]["data"]
            interval_start_timestamp=0
            got_it = 0
            intervals_temp = {}

            trial=1
            timestamps_temp = {}

            for timestamp in sorted(result_set.keys()):
                if "101" in result_set[timestamp] :
#                    print("got 101: timestamp: "+str(timestamp))
                    got_it = 1
                    interval_start_timestamp = timestamp

                    timestamps_temp[trial] = {}
                    timestamps_temp[trial]["101"] = timestamp
                    continue

                if got_it == 1 and "102" in result_set[timestamp] :
#                    print("got 102 after 101: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals_temp["101-102"]=interval
#                   print("writing interval: "+ str(interval))
                    interval_start_timestamp = timestamp

                    timestamps_temp[trial]["102"] = timestamp

                    got_it = 2 
                    continue
                elif got_it == 1 :
                    intervals_temp = {}
                    timestamps_temp[trial] = {}
                    got_it = 0
                    

                if got_it == 2  and "103" in result_set[timestamp] :
#                    print("got 103 after 102: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals_temp["102-103"]=interval
#                   print("writing interval: "+ str(interval))
                    interval_start_timestamp = timestamp

                    timestamps_temp[trial]["103"] = timestamp

                    got_it = 3 
                    continue
                elif got_it == 2 :
                    intervals_temp = {}
                    timestamps_temp[trial] = {}
                    got_it = 0
                    

                if got_it == 3  and "104" in result_set[timestamp] :
#                    print("got 104 after 103: timestamp "+ str(timestamp))
                    interval = timestamp - interval_start_timestamp
                    intervals_temp["103-104"]=interval

                    timestamps_temp[trial]["104"] = timestamp

                    #INTERVALS
#                    print("writing intervals!")
                    #all cool, append intervals_temp to intervals
                    for i in intervals_temp.keys():
                        intervals[mid][d][i].append(intervals_temp[i])


                    #TIMESTAMPS
                    timestamps[mid][d][trial] = {}
#                    print("trial: "+ str(trial))
#                    print(json.dumps(timestamps_temp[trial],indent=4))
                    for k in timestamps_temp[trial].keys() :
                        timestamps[mid][d][trial][k] = timestamps_temp[trial][k]

                    interval_temp = {}
                    got_it = 0
                    trial = trial+1
                    continue
                elif got_it == 3 :
                    intervals_temp = {}
                    timestamps_temp[trial]= {}
                    got_it = 0
                    

#            for t in timestamps[mid][d].keys():
#                print("trial: " + str(t) +" 101:"+str(timestamps[mid][d][t]["101"])
#                                +" 102: "+str(timestamps[mid][d][t]["102"])
#                                +" 103: "+str(timestamps[mid][d][t]["103"])
#                                +" 104: "+str(timestamps[mid][d][t]["104"]) )


            #INTERVALS
            #count average per day
            for v in intervals[mid][d]["101-102"] :
                results[mid][d]["101-102"]={}
                results[mid][d]["101-102"]["avg"]= mean(intervals[mid][d]["101-102"])
                results[mid][d]["101-102"]["med"]= median(intervals[mid][d]["101-102"])

            for v in intervals[mid][d]["102-103"] :
                results[mid][d]["102-103"]={}
                results[mid][d]["102-103"]["avg"]= mean(intervals[mid][d]["102-103"])
                results[mid][d]["102-103"]["med"]= median(intervals[mid][d]["102-103"])

            for v in intervals[mid][d]["103-104"] :
                results[mid][d]["103-104"]={}
                results[mid][d]["103-104"]["avg"]= mean(intervals[mid][d]["103-104"])
                results[mid][d]["103-104"]["med"]= median(intervals[mid][d]["103-104"])


        
     #TIMESTAMPS
    results2={}
    for mid in my_dataset.keys():
        results2[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results2[mid][d]={}
            for t in timestamps[mid][d].keys():
                #structure - mid - d - t - code - start_ts - end_ts - normalized_start_ts - normalized_end_ts - interval
                results2[mid][d][t]={}

                #add 101-102
                ts_101 = timestamps[mid][d][t]["101"]
                code="101-102"
                results2[mid][d][t][code]={}
                results2[mid][d][t][code]["start_ts"] = ts_101
                results2[mid][d][t][code]["end_ts"] = timestamps[mid][d][t]["102"]
                results2[mid][d][t][code]["start_ts"] = timestamps[mid][d][t]["101"]
                results2[mid][d][t][code]["normalized_start_ts"] = timestamps[mid][d][t]["101"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["normalized_end_ts"] = timestamps[mid][d][t]["102"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["interval"] = results2[mid][d][t][code]["end_ts"] - results2[mid][d][t][code]["start_ts"]
           
                #add 102-103
                code="102-103"
                results2[mid][d][t][code]={}
                results2[mid][d][t][code]["start_ts"] = timestamps[mid][d][t]["102"]
                results2[mid][d][t][code]["end_ts"] = timestamps[mid][d][t]["103"]
                results2[mid][d][t][code]["start_ts"] = timestamps[mid][d][t]["102"]
                results2[mid][d][t][code]["normalized_start_ts"] = timestamps[mid][d][t]["102"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["normalized_end_ts"] = timestamps[mid][d][t]["103"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["interval"] = results2[mid][d][t][code]["end_ts"] - results2[mid][d][t][code]["start_ts"]

                #add 103-104
                code="103-104"
                results2[mid][d][t][code]={}
                results2[mid][d][t][code]["code"]="103-104"
                results2[mid][d][t][code]["start_ts"] = timestamps[mid][d][t]["103"]
                results2[mid][d][t][code]["end_ts"] = timestamps[mid][d][t]["104"]
                results2[mid][d][t][code]["start_ts"] = timestamps[mid][d][t]["103"]
                results2[mid][d][t][code]["normalized_start_ts"] = timestamps[mid][d][t]["103"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["normalized_end_ts"] = timestamps[mid][d][t]["104"] - ts_101 #should be 0 :-D
                results2[mid][d][t][code]["interval"] = results2[mid][d][t][code]["end_ts"] - results2[mid][d][t][code]["start_ts"]


#    print(json.dumps(results2,indent=4))
#    print(json.dumps(intervals,indent=4))
#    print(json.dumps(results,indent=4))

    #INTERVALS
    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')

        csvwriter.writerow(["#Intervals in correct attempts - mean and median"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)",
                            "average interval 101-102 [s]", "average interval 102-103 [s]", "average interval 103-104 [s]",
                            "median interval 101-102 [s]", "median interval 102-103 [s]", "median interval 103-104 [s]"])
        csvwriter.writerow(["mid", "grp","day","date",
                            "avg_interval-101-102", "avg_interval-102-103", "avg_interval-103-104",
                            "med_interval-101-102", "med_interval-102-103", "med_interval-103-104"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    try:
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], 
##                                            results[m][d]["101-102"]["avg"]/100,results[m][d]["102-103"]["avg"]/100,results[m][d]["103-104"]["avg"]/100,
                                            results[m][d]["101-102"]["med"]/100,results[m][d]["102-103"]["med"]/100,results[m][d]["103-104"]["med"]/100])
                    except KeyError:
                        continue

    #TIMESTAMPS
    #output
    with open(output_file2, "w", newline='') as csvfile2:
        csvwriter = csv.writer(csvfile2, delimiter=',')

        csvwriter.writerow(["#Timestamps in correct attempts"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)",
                            "trial",
                            "operation code",
                            "start timestamp [10 ms]", "end timestamp [10ms]",
                            "normalized start timestamp [10ms]", "normalized end timestamp [10ms]",
                            "interval [10ms]"])
        csvwriter.writerow(["mid", "grp","day","date",
                            "trial",
                            "code",
                            "start_ts","end_ts",
                            "normalized_start_ts", "normalized_end_ts",
                            "interval"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results2[m].keys():
                    for t in results2[m][d].keys():
                        for c in results2[m][d][t].keys():
                            try:
                                csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], 
##                                                    results[m][d]["101-102"]["avg"]/100,results[m][d]["102-103"]["avg"]/100,results[m][d]["103-104"]["avg"]/100,
                                                    t,
                                                    c,
                                                    results2[m][d][t][c]["start_ts"], results2[m][d][t][c]["end_ts"],
                                                    results2[m][d][t][c]["normalized_start_ts"], results2[m][d][t][c]["normalized_end_ts"],
                                                    results2[m][d][t][c]["interval"]])
                            except KeyError:
                                continue

#analyze bouts and pauses
def analyze_bouts_and_pauses(task, interval=6000):


    print("analyze: bouts (pause:"+str(interval)+")")
    subanalysis_name="bouts-pause-"+str(interval) 

    input_file = './data/data_by_task/task-'+task+'.csv'
    print("Input file: "+input_file)

    csvfile = open(input_file, newline='')

    my_dataset = data_loader.file_load(csvfile)
    data_summary = data_loader.process_summary(my_dataset)

    output_path="./data/subanalysis_results/"+subanalysis_name+"/" 
    if not os.path.exists(output_path): 
        os.makedirs(output_path) 

    #output_session_time='./data/analysis_results/'+task+'-session_time.csv'
    output_file= output_path+task+'-'+subanalysis_name+".csv"


    #go through dataset timestamps, look for pauses longer than interval
    results={}
    for mid in my_dataset.keys():
        results[mid]={}
        for d in sorted(my_dataset[mid].keys()):
            results[mid][d]=[]
            result_set = my_dataset[mid][d]["data"]

            first_ts = 0
            previous_ts=0

            for timestamp in sorted(result_set.keys()):
                #works with array of codes too now...

                #check if we have pause
                if timestamp - previous_ts > interval :
                    
                    #pause found
 #                   print("BOUT: first_ts:"+ str(first_ts) + " last_ts:"+ str(previous_ts) + " --> time:"+data_loader.get_timestamp(previous_ts-first_ts))
                    results[mid][d].append({"type":"BOUT","first_ts":first_ts,"last_ts":previous_ts,"duration":previous_ts-first_ts})
#                    print("PAUSE: first_ts:"+ str(previous_ts) + " last_ts:"+ str(timestamp)+ " --> time:"+data_loader.get_timestamp(timestamp-previous_ts))
                    results[mid][d].append({"type":"PAUSE","first_ts":previous_ts,"last_ts":timestamp,"duration":timestamp-previous_ts})
                    first_ts = timestamp
                    previous_ts = timestamp

                else:
                    #look for code 3 for end of session (either successful or timeout), may end with pause but this will be recognized in code above..
                    for code in sorted(result_set[timestamp]):
                       if code in ["3"]:
#                            print("FINAL BOUT: first_ts:"+ str(first_ts) + " last_ts:"+ str(timestamp) + " --> time:"+data_loader.get_timestamp(previous_ts-first_ts))
                            results[mid][d].append({"type":"BOUT","first_ts":first_ts,"last_ts":timestamp,"duration":timestamp-first_ts})
                            break
    
                    #no change
                    previous_ts = timestamp

#    print(json.dumps(results,indent=4)) 

    #output
    with open(output_file, "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
   
        csvwriter.writerow(["#Bouts and Pauses ["+str(interval)+"]"])
        csvwriter.writerow(["#mouse id", "group", "day","date (yymmdd)","bout/pause","start (timestamp)","end (timestamp)","duration (10ms)"])
        csvwriter.writerow(["mid", "grp","day","b-p","start_ts","end_ts","duration"])

        #group
        for g in mice_order:
            #mouse
            for m in mice_order[g]:
                #day
                for d in results[m].keys():
                    for i in range(len(results[m][d])): 
                        csvwriter.writerow([m,g,d,my_dataset[m][d]["metadata"]["date"], 
                            results[m][d][i]["type"],
                            results[m][d][i]["first_ts"],
                            results[m][d][i]["last_ts"],
                            results[m][d][i]["duration"]
                            ])

#just a little helper ;-)
def run_all(task):
    analyze_response_codes_per_interval(t,correct_presses+incorrect_presses)
    analyze_response_codes_per_trial(t,correct_presses+incorrect_presses)
    analyze_response_codes_per_interval_incremental(t, correct_presses, "correct")
    analyze_response_codes_per_interval_incremental(t, incorrect_presses, "incorrect")
    analyze_response_codes_per_interval_incremental(t, in_timeout_presses, "in_timeout")
    analyze_response_codes_per_interval_incremental(t, correct_presses+incorrect_presses+in_timeout_presses, "all")
    analyze_response_codes_per_interval_incremental(t, ["2"], "reinforcement")
    analyze_trial_times(t)
    
    analyze_trial_time(t)
    count_completed_trials(t)
    count_all_presses(t)
    count_correct_presses(t)
    count_incorrect_presses(t)
    count_in_timeout_presses(t)

    analyze_sequences(t)
    analyze_interval_102_103(t)    
    analyze_interval_103_104(t)
    analyze_interval_2_x(t)
    analyze_interval_correct_sequence(t)
    analyze_bouts_and_pauses(t,6000)



#pretty print
#print(json.dumps(data_summary, indent=4))
for t in tasks_list:
    print("----TASK----:"+t)
#    analyze_response_codes_per_interval(t,correct_presses+incorrect_presses)
#     analyze_response_codes_per_trial(t,correct_presses+incorrect_presses)
#    analyze_response_codes_per_interval_incremental(t, correct_presses, "correct")
#    analyze_response_codes_per_interval_incremental(t, incorrect_presses, "incorrect")
#    analyze_response_codes_per_interval_incremental(t, in_timeout_presses, "in_timeout")
#    analyze_response_codes_per_interval_incremental(t, correct_presses+incorrect_presses+in_timeout_presses, "all")
#    analyze_response_codes_per_interval_incremental(t, ["2"], "reinforcement")
#     analyze_trial_times(t)

#    analyze_trial_time(t)
#    count_completed_trials(t)
#    count_all_presses(t)
#     count_correct_presses(t)
#     count_incorrect_presses(t)
#     count_in_timeout_presses(t)

#     sequences = test_sequences(t)
#     seq_results = count_sequences_by_day(sequences)
#     print(json.dumps(seq_results, indent = 4))
#     analyze_sequences(t)
#     analyze_interval_102_103(t)    
#     analyze_interval_103_104(t)
#     analyze_interval_2_x(t)
#    analyze_interval_correct_sequence(t)
#     analyze_bouts_and_pauses(t,6000)

    #or RUN IT ALL ;-)
    run_all(t)
