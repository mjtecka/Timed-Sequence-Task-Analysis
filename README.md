# Timed sequence task - Analysis

Python scripts that analyze specific aspects of tasks logs, generated by operant boxes.

Operant boxes code and data are provided separately.  

Code is licensed under FreeBSD license. 

## How to run the scripts
1) download scripts
2) download the original data from [dataset_DOI_]

3) add original data into data directory (./data/original_data) 
   - mastersheet_complete_one_file.csv, data_vpa_final.csv (default)
4) run mastersheet_matcher.py
   - mastersheet_matcher will create separate log files for all tasks, using mastersheet_complete_one_file.csv and data_vpa_final.csv 
5) run analyzer.py 
   - analyzer will create specified subanalyses data in ./data/subanalysis_results directory


## Scripts:

### mastersheet_matcher.py
- filters logs from all tasks by task names into respective files
- mastersheet CSV record has following structure: mouse_id; date(DD.MM.YY); task_name 

### data_loader.py
- loads data from logs into JSON format
- JSON format allows better access to the data and is used in analyzer.py 
- specific mouse ids are defined in data_loader.py


### analyzer.py
- uses data in JSON format for running many kinds of subanalyses; new kinds of subanalyses can be added 

subanalyses (of data from task "t"):

analyze_trial_time(t)
- get session duration (time to complete 40 trials)
    
count_completed_trials(t)
- get number of successfully completed trials (rewards)

count_all_presses(t)
- count all presses in trial and per reinforcement

count_correct_presses(t)
- count correct presses in trial and per reinforcement

count_incorrect_presses(t)
- count incorrect presses in trial and per reinforcement

count_in_timeout_presses(t)
- count incorrect presses in trial and per reinforcement

analyze_sequences(t)
- analyze all press sequences per day

analyze_interval_102_103(t)    
- analyze interval between 102 and 103 per day (LL(?)P)

analyze_interval_103_104(t)
- analyze interval between 103 and 104 per day ((LLP(?)P)

analyze_interval_2_x(t)
- analyze interval after reinforcement (2-x)
 
analyze_interval_correct_sequence(t)
- analyze intervals in correct sequence 101->?->102->?->103->?->104
- analyze timestamp in correct sequence 101->?->102->?->103->?->104

analyze_bouts_and_pauses(t,6000)
- analyze bouts and pauses by interval

analyze_response_codes_per_interval(t,correct_presses+incorrect_presses)
- look for correct presses and puts them into "buckets" by time interval

analyze_response_codes_per_trial(t,correct_presses+incorrect_presses)
- look for correct and incorrect presses and put them into "buckets" by trial

analyze_response_codes_per_interval_incremental(t, correct_presses, "correct")
- incrementaly look for correct presses  and put them into "buckets" by trial

analyze_response_codes_per_interval_incremental(t, incorrect_presses, "incorrect")
- incrementaly look for incorrect presses  and put them into "buckets" by trial

analyze_response_codes_per_interval_incremental(t, in_timeout_presses, "in_timeout")
- incrementaly look for presses during time out  and put them into "buckets" by trial

analyze_response_codes_per_interval_incremental(t, correct_presses+incorrect_presses+in_timeout_presses, "all")
- incrementaly look for all presses and put them into "buckets" by trial

analyze_response_codes_per_interval_incremental(t, ["2"], "reinforcement")
-  incrementaly look for reinforcements and put them into "buckets" by trial

