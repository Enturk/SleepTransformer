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
import datetime

#to create timestamps for filenames
import time
ts = time.gmtime()
timestamp = time.strftime("%Y-%m-%d+%H-%M-%S", ts)

# main variables
in_file = "Scoring Tab Export_DailyDetailed.csv"
input_dir = "Scoring Tab Export\\Scoring Tab Export"
output_dir = "BatchTransformOutput"
out_file = "Actigraph"
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

out_file = output_dir + "\\" + out_file + timestamp + ".csv"

# Main
# unused stuff kept in case something breaks:
# in_file = os.listdir(input_dir)[0] # FIXME puts a 'b' in front of file name...
# in_file = "C:\\Users\\nazim\\Documents\\PSS\\BatchSleepExportDetails\\BatchSleepExportDetails(2019-03-12_10-01-53).csv"

dateparse = lambda x: pd.datetime.strptime(x, '%m/%d/%Y')
columns = ['Subject', 'Date', 'kcals', 'METs', 'Sedentary', 'Light', 'Moderate', 'Vigorous', 'Very Vigorous',
    '% in Sedentary', '% in Light', '% in Moderate', '% in Vigorous', '% in Very Vigorous', 'Steps Counts']
datetime_columns = ['Date']
first_file = True
out_df = pd.DataFrame()

# go through each file to extract data from
os.chdir(input_dir)
for file_name in glob.iglob(in_file, recursive=True):
    if verbose:
        print("Processing: " + file_name)
    # export data
    in_df = pd.read_csv(file_name, parse_dates=datetime_columns, date_parser=dateparse)[columns].copy()
    if verbose:
        print(in_df.tail())
    out_df = out_df.append(in_df, ignore_index = True)
    if verbose:
        print("Cumulative dataframe:")
        print(out_df.tail())

# remove duplicate rows
out_df = out_df.drop_duplicates(keep='first')

# transform the fields that weren't provided
##out_df['Total Time in Bed'] = out_df['Total Sleep Time']
##out_df['Total Sleep Time'] = out_df['Total Time in Bed']-out_df['Length of Awakenings in Minutes']-out_df['Latency']
##out_df['Mid-Sleep Point'] = out_df['Onset'] + (out_df['Out Bed Time']-out_df['Onset'])/2 # TODO review if this is correct!
##out_df['Date'] = out_df['In Bed Time'].dt.date

# if you're reading all this, then here's a rewarding gif: https://i.imgur.com/vaoNp2b.gif

# prep for missing dates
if verbose:
    print(out_df.tail())
    out_df.info(verbose = True)
subject = ""
missing_rows = []
# FIXME
### check for missing dates:
##for i, row in out_df.iterrows():
##    if verbose:
##        print("Subject: " + subject)
##    if row['Subject Name'] == subject:
##        if row['Date'] == expected_date:
##            expected_date += datetime.timedelta(days=1)
##        else:
##            if verbose:
##                print("Missing date: " + str(expected_date))
##                print("Current row's date: " + str(row['Date']))
##            # figure out date difference in days
##            date_diff = (row['Date'] - expected_date).days
##            print(str(date_diff) + " days difference.")
##            count = 0
##            while(date_diff > count):
##                # create row
##                line = {'Subject Name': subject,
##                        'In Bed Time':None, 'Out Bed Time':None, 'Efficiency':None, 'Latency':None,
##                        'Onset':None, 'Total Sleep Time':None,'WASO':None, 'Number of Awakenings':None,
##                        'Length of Awakenings in Minutes':None, 'Total Time in Bed':None, 'Mid-Sleep Point':None,
##                        'Date': expected_date}
##                if verbose:
##                    print(line)
##                missing_rows.append(line)
##                # update expected_date
##                expected_date += datetime.timedelta(days=1)
##                count += 1
##            if verbose:
##                break
##    else:
##        # new subject, new everything!
##        subject = row['Subject Name']
##        expected_date = row['Date']
##        expected_date += datetime.timedelta(days=1)
### merge missing dataframe
##if verbose:
##    print("Missing dates:")
##    print(missing_rows)
##
### out_df = pd.concat([out_df,missing_df])
##out_df = out_df.append(pd.Dataframe(missing_rows), ignore_index = True, sort=False) # FIXME module 'pandas' has no attribute 'Dataframe
if verbose:
    print("End of dataframe with missing dates:")
    print(out_df.tail())
# resort dataframe
# out_df = pd.MultiIndex.from_product([out_df['Subject Name'].unique()], names=['Subject Name', 'Date']) # FIXME Length of names must match number of levels in MultiIndex

# load the data
out_df.to_csv(out_file)

# cleanup of output
if numberOfFiles == 0:
    log_file.close()
    sys.stdout = old_stdout
