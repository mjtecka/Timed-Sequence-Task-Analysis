### Mastersheet matcher / operant box - mice experiments [Krabimyše]
# 
#
#   Code: Milan Janíček <mjtecka@gmail.com>
#   
#   input - data & mastersheet - from ./data/original_data/
#   output - csv for experiments - into ./data/data_by_task/
#
#   matches experimental data (from operant box) with mastersheet data (=which task was performed when)
#   outputs csv files for all detected tasks
#   
###

import csv
import json
import os
import re

#--configuration--
mastersheet_filename="./data/original_data/mastersheet-boxove-mysi_complete_one_file.csv"
data_filename = './data/original_data/data_vpa_final.csv'
#--


ms_file = open(mastersheet_filename, newline='')
my_mastersheet={}

data_file = open(data_filename, newline='')
my_data={}

#loads one row from master sheet
def ms_row_load(row, mastersheet):
    mouse_id=row.pop(0).lower()

    #modify date
    date=row.pop(0)
    d = re.split("\.",date)
    day=d[0].zfill(2)
    month=d[1].zfill(2)
    ylength=len(d[2])
    year=d[2][ylength-2:]
    date = year + month + day
    
    task=row.pop(0)

    try:
       mastersheet[mouse_id]
    except KeyError:
       # KeyError -> this is first row for this mouse, create new dir in dataset & set day to 1 
       mastersheet[mouse_id]={}


    mastersheet[mouse_id][date]=task

#loads master sheet into JSON format
def ms_file_load(csvfile):
#load file
 # process each line
   # mouseID -> data
    filereader = csv.reader(csvfile, dialect='excel',delimiter=';')
    for row in filereader:
        ms_row_load(row, my_mastersheet)
    
    return my_mastersheet


#combines data with previously loaded mastersheet
def data_file_process(csvfile,mastersheet):
    filereader = csv.reader(csvfile,delimiter=',')
    found=0
    not_found=0

    for row in filereader:        
        #get mouse_id and date
        mouse_id = row[0].lower()
        date = row[1]
        #find task 
        try:
            task = mastersheet[mouse_id][date]
            found +=1
        except KeyError:
            not_found +=1
            print ("ERROR: task not found for mouse_id: " + mouse_id + " date:  " +date)
            continue

        print("task found: + [" + task + "] for mouse_id: " + mouse_id + " date:  " +date)

        #open task file, write row, close task file
        task=task.replace("/","_")
        task=task.replace("  ","-")
        task=task.replace(" ","-")
        
        #data will go here:
        filename = "./data/data_by_task/task-"+task+".csv"
        with open(filename,'a+') as f :
            csv_writer = csv.writer(f, delimiter=',')
            csv_writer.writerow(row)
        f.close()

    print("summary: tasks found: "+str(found) +" not found:"+ str(not_found))


#---- MAIN ---

my_mastersheet = ms_file_load(ms_file)

#print mastersheet json
#print(json.dumps(my_mastersheet, indent=4))


folder = './data/data_by_task/'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
#        elif os.path.isdir(file_path):
#            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))



data_file_process(data_file, my_mastersheet)
