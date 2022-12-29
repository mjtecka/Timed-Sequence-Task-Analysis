### Data loader / operant box - mice experiments [Krabimyše]
# 
#
#   Code: Milan Janíček <mjtecka@gmail.com>
#   
#   input - csv file
#   output - json data structure
#
#
#   Transforms data from format used by operant box software into JSON structure. This allows easier analysis of results.
#   analyzer.py uses this code for loading data - this script doesn't have to be run separately
###

import csv
import json
import sys


#how many rows do we need to ignore in export? / in which column real data start?
DATA_START_IN_CSV=58
my_dataset={}

#--configuration--
#-input file-
## select input file, SoftCR csv ("," separated is expected)
#input_file = './data/_test_data/tropi_vs_saline_LLR-mod.csv'
#input_file = './data/_test_data/sample_100.csv'
input_file = './data/original_data/data_vpa_final.csv'


#-mice order-
#NOTE mice_order is important, sets up mice identifiers and group membership NOTE
## set up specific order of mice in output
mice_order={}
#mice_order["grp1"]= ["c6m1","c6m5","c7m1","c7m3","c8m1"]
mice_order["saline"] = [ "c39am1", "c39bm2", "c39bm3", "c39am4", "c39am5", "c41am1", "c41am2", "c41am3", "c41bm4", "c41bm5", "c41bm6"]
mice_order["VPA"] = [ "c40am1", "c40am2", "c40bm3", "c40am4", "c40bm5", "c40bm6", "c45am1", "c45am2", "c45am3", "c45bm4", "c45bm5"]
mice_list_order=[]
#-----


#doesn't make sense with only one group, but would work with 2 or more as well ;-)
for gr in mice_order.keys():
    for i in mice_order[gr]:
        mice_list_order.append(i)
#print (mice_list_order)

#open file
csvfile = open(input_file, newline='')

#loads data from operant box export - NOTE this format may differ in regard to data export options in operant box software!
def row_load(row, dataset):
    #get mouse_id, NOTE lowercase may be needed due possible inconsistency in data..
    mouse_id = row.pop(0).lower()
    exp_data={}
    #/print ("mouse_id: ")

    day=""
    #for runs in multiple days - get number of day 
    #check if mouse_id exists; if not, then day = 1, if it does check length of 
    try:
       day = len(dataset[mouse_id].keys()) + 1
    except KeyError:
       # KeyError -> this is first row for this mouse, create new dir in dataset & set day to 1 
       day = 1
       dataset[mouse_id]={}

    #get some metadata from line, throw away rows until experiment data
    dataset[mouse_id][day]={}
    dataset[mouse_id][day]["metadata"]={}
    dataset[mouse_id][day]["metadata"]["date"]=row.pop(0)
    dataset[mouse_id][day]["metadata"]["time"]=row.pop(0)
    #throw away more - depends on export format
    row.pop(DATA_START_IN_CSV-3)
    row = row[DATA_START_IN_CSV-3:]

    dataset[mouse_id][day]["data"]=""
    #get experiment_data
    timestamp=0
    for ed in row :

        #testing (try) for C(xxx) values
        try:
            #parse X.Y number into pairs (time_diff, value)
            (time_diff, value) = ed.split(".")
            # print ("TD: "+ time_diff, " VAL: " + value)

            #add real time to time diff & save pair into dict
            #add dict into data array
            exp_timestamp=timestamp+int(time_diff)

            #skip value, if something with this timestamp exists (TODO describe)
            if exp_data.get(exp_timestamp)==None:
                exp_data[exp_timestamp]= [value]
            else :
                exp_data[exp_timestamp].append(value)

        except ValueError:
     #       print("C(xx) found - ValueError thrown and caught")
            #sys.stderr.write("C(xx) found - ValueError thrown and caught")
            break

        #change timestamp
        timestamp = exp_timestamp

    #print (exp_data)
    dataset[mouse_id][day]["data"] = exp_data

#loads file with data, returns my_dataset in JSON
def file_load(csvfile):
#load file
 # process each line
   # mouseID -> data
    my_dataset={} #TODO my_dataset needs to be reset this way, should be refactored to use variables more sensibly...
    filereader = csv.reader(csvfile, delimiter=',')
    for row in filereader:
        row_load(row, my_dataset)
    
    return my_dataset

#creates summary JSON with mouse id, day, session number, date & time
def process_summary(dataset):
    summary_json={}
    for mouse_id in dataset :
        summary_json[mouse_id]={}

        for day in dataset[mouse_id]:
            summary_json[mouse_id][day]={}

            summary_json[mouse_id][day]["metadata"]=dataset[mouse_id][day]["metadata"]
    return summary_json

#---tools---
#returns formated timestamp
def get_timestamp(timestamp):
    #software works with 10ms
    timestamp = int(timestamp)*10
    seconds=(timestamp/1000)%60
    seconds = int(seconds)
    #minutes=(timestamp/(1000*60))%60
    minutes=(timestamp/(1000*60))
    minutes = int(minutes)
    hours=(timestamp/(1000*60*60))%24

    #return ("%dh:%dm:%ds" % (hours, minutes, seconds))
    return ("%dm:%ds" % (minutes, seconds))


#---main---
## this code can be run for testing purposes - it only prints data in JSON format
if __name__ == '__main__':

    my_dataset=file_load(csvfile)
    #- pretty print
    print(json.dumps(my_dataset, indent=4))
    #- normal print 
    #print(json.dumps(my_dataset))


    #playing around

#    summary_json={}
#    for mouse_id in my_dataset :
#        summary_json[mouse_id]={}
#        for day in my_dataset[mouse_id]:
#            summary_json[mouse_id][day]={}
    
#            summary_json[mouse_id][day]["metadata"]=my_dataset[mouse_id][day]["metadata"]

    summary_json = process_summary(my_dataset)
    print(json.dumps(summary_json, indent=4))

