#!/usr/bin/env python
# Made by nazim@karaca.org ...

# TODO make self-executable: https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263

import sys
import getopt
import os
#import hashlib
#import requests
import pandas as pd
import glob

#to create timestamps for filenames
import time
ts = time.gmtime()
timestamp = time.strftime("%Y-%m-%d+%H-%M-%S", ts)

# main variables
input_dir = "BatchSleepExportDetails"
output_dir = "BatchTransformOutput"

# testing done on a small number of known files
# set to 0 if not testing
numberOfFiles = 1
verbose = True
# TODO: change these defaults to better defaults

# parse command line options
try:
    options, remainder = getopt.getopt(
        sys.argv[1:],
        'i:o:t:v',
        ['input=',
         'output=',
         'testing=',
         'verbose',
         ])
except getopt.GetoptError as err:
    print('ERROR:', err)
    print('The only options this script can process are:')
    print(
        '-i or --input [input directory]: use [input directory] instead of', input_dir)
    print(
        '-o or --output [output directory]: use [output directory] instead of', output_dir)
    print(
        '-t or --testing [integer]: run in test mode, only process first [integer] files in input directory')
    print('-v or --verbose: very verbose feedback on script activity')
    sys.exit(1)

for opt, arg in options:
    if opt in ('-i', '--input'):
        # TODO check if csv files in here
        input_dir = arg
    elif opt in ('-o', '--output'):
        output_dir = arg
    elif opt in ('-t', '--testing'):
        numberOfFiles = int(arg)
    elif opt in ('-v', '--verbose'):
        verbose = True

import sys
if numberOfFiles == 0:
    old_stdout = sys.stdout
    log_file = open("message.log", "w")
    sys.stdout = log_file

if verbose:
    print('ARGV            : ', sys.argv[1:])
    print('Input Directory : ', input_dir)
    print('Output Directory: ', output_dir)
    print('Number of files : ', numberOfFiles)
    print('Verbose         : ', verbose)
    print('REMAINING       : ', remainder)

# for folder navigation
# script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
script_dir = os.getcwd()
if os.path.exists(os.path.join(script_dir, input_dir)):
    input_dir = os.path.join(script_dir, input_dir)
    print(f'Current input directory is {input_dir}')
else:
    print(f'Fatal error - input directory {input_dir} not found')
    quit()
if os.path.exists(os.path.join(script_dir, output_dir)):
    output_dir = os.path.join(script_dir, output_dir)
    print(f'Current output directory is {input_dir}')
else:
    print(f'Fatal error - output directory {output_dir} not found')
    quit()

out_file = output_dir + "\\BatchTransform_" + timestamp + ".csv"

# Main
# unused stuff kept in case something breaks:
# in_file = os.listdir(input_dir)[0] # FIXME puts a 'b' in front of file name...
# in_file = "C:\\Users\\nazim\\Documents\\PSS\\BatchSleepExportDetails\\BatchSleepExportDetails(2019-03-12_10-01-53).csv"

dateparse = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %H:%M:%S %p')
columns = ['Subject Name', 'In Bed Time', 'Out Bed Time', 'Efficiency', 'Latency', 'Onset', 'Total Sleep Time', 'WASO', 'Number of Awakenings', 'Length of Awakenings in Minutes']
datetime_columns = ['In Bed Time', 'Out Bed Time', 'Onset']
first_file = True
out_df = pd.DataFrame()
    
# go through each file to extract data from
os.chdir(input_dir)
for file_name in glob.iglob("*.csv", recursive=True):
    if verbose:
        print("Processing: " + file_name)
    # export data
    in_df = pd.read_csv(file_name, parse_dates=datetime_columns, date_parser=dateparse)[columns].copy()
    if verbose:
        print(in_df)
    out_df = out_df.append(in_df, ignore_index = True)
    if verbose:
        print("Cumulative dataframe:")
        print(out_df)

# remove duplicate rows
out_df = out_df.drop_duplicates(keep='first') # subset=['Subject Name', 'In Bed Time'], 

# insert null rows for missing days

# transform the fields that weren't provided
out_df['Total Time in Bed'] = out_df['Total Sleep Time']
out_df['Total Sleep Time'] = out_df['Total Time in Bed']-out_df['Length of Awakenings in Minutes']-out_df['Latency']
out_df['Mid-Sleep Point'] = out_df['Onset'] + (out_df['Out Bed Time']-out_df['Onset'])/2 # TODO review if this is correct!

#open file to put data out into
out_df.to_csv(out_file)

# cleanup of output
if numberOfFiles == 0:
    log_file.close()
    sys.stdout = old_stdout
