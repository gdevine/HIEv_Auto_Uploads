'''
Python script to perform automated data uploads into the HIEv application.

Using this script, a user can dump files (with a file naming convention applied) into the 
Data directory and use the file_settings.yaml file to specify regex matching patterns against 
those files. Upin successful upload into HIEv the matched files are moved out of the Data directory
and into the Backups folder.   

This script expects a folder named 'Data' and a folder named 'Backups' at the same level as this 
script to work.
  

Author: Gerard Devine
Date: January 2016
'''


import os
from datetime import date, datetime, timedelta
import re
import requests
import shutil
import yaml


# --Open log file for writing and append date/time stamp into file for a new entry
logfile = 'log.txt'
log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), logfile), 'a')
log.write('\n----------------------------------------------- \n')
log.write('------------  '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'  ------------ \n')
log.write('----------------------------------------------- \n')
log.write('\n')


# -- Assign directory where source data will be found as well as a backups directory to store a copy of uploaded data.
# data_dir = os.path.join(os.path.dirname(__file__), 'Data')
# backup_dir = os.path.join(os.path.dirname(__file__), 'Backups')
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')
backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Backups')
    
                
def extract_date(file, position):
    ''' Function to split a filename string (file) and use the position parameter 
    to pull out a date or daterange. Thus date or daterange is then converted to a 
    HIEv-friendly start_time and end_time
    ''' 
    
    #removing the file ending from the filename
    filename_no_ending = file.split('.')[0]
    #split the filename into different parts by the '_' seperator
    filename_split = filename_no_ending.split('_')
    #pull out the date or daterange using the supplied position 
    datestring = filename_split[position]
    # check that the extracted date (or daterange) is of the form YYYYMMDD or YYYYMMDD-YYYYMMDD
    if re.match('^[0-9]{8}$|^[0-9]{8}-[0-9]{8}$', datestring):
        # if only a single date is given tailor the start time and end time accordingly
        if len(datestring) == 8:
            start_time = '%s-%s-%s 00:00:00' % (datestring[0:4], datestring[4:6], datestring[6:8]) 
            end_time = '%s-%s-%s 11:59:59' % (datestring[0:4], datestring[4:6], datestring[6:8]) 
        # if a date range is given tailor the start time and end time accordingly
        elif len(datestring) == 17:
            startdate = datestring.split('-')[0]
            start_time = '%s-%s-%s 00:00:00' % (startdate[0:4], startdate[4:6], startdate[6:8])
            enddate = datestring.split('-')[1]
            end_time = '%s-%s-%s 11:59:59' % (enddate[0:4], enddate[4:6], enddate[6:8])
        
        # pass back the resulting start and end times to the calling routine     
        return start_time, end_time
    else:
        print 'this is not a valid date or date range' 


# Begin by loading in information from Yaml file            
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "file_settings.yaml"), 'r') as yamlfile:
    matcher_info = yaml.safe_load(yamlfile)
    # Grab api token from yaml file for making calls to HIEv
    api_token = matcher_info['api_token']
    # Append api token to base URL to generate full HIEv upload API request  
    upload_url = 'https://hiev.uws.edu.au/data_files/api_create.json?auth_token='+api_token
    
    # Loop through all files in the Data directory 
    for file in os.listdir(data_dir):
        # Loop through all matches patterns from the yaml file 
        for matcher in matcher_info['matchers']:
            # If a given file matches the current pattern proceed to upload to HIEv
            if re.match(matcher['match'], file):
                log.write(' Match found - %s \n' % (file) )
                # prepare the file for uploading via the HIEv API
                upload_file = {'file': open(os.path.join(data_dir, file), 'rb')}
                # Extract start and end times if required by passing the filename and date position 
                # to the extract_date function
                if matcher['extract_date'] == 'True':
                    start_time, end_time = extract_date(file, matcher['date_position'])
                      
                # Compile available metadata 
                payload = {'type':matcher['filetype'], 
                           'experiment_id': matcher['experiment_id'], 
                           'start_time': start_time, 
                           'end_time': end_time, 
                           'description': matcher['description'], 
                           'format':matcher['format'] }
                
                # Upload file and associated metadata to HIEv
                r = requests.post(upload_url, files=upload_file, data=payload, verify=False)
                
                # If the upload was successful move the original file from the data folder
                # to the backup folder 
                if r.status_code == 200:
                    log.write(' File successfully uploaded to HIEv \n' )
                    upload_file['file'].close()
                    try:
                        #shutil.move(str(os.path.join(data_dir, file)), str(os.path.join(backup_dir, file)))
                        shutil.move(os.path.join(data_dir, file), os.path.join(backup_dir, file))
                        log.write(' File moved from Data folder to Backup folder \n' )
                    except:
                        print 'there was an error'
                        log.write(' ERROR - There was a problem moving the file to the Backup folder \n' )
                else:
                    log.write(' ERROR - There was a problem uploading the file to HIEv \n' )


# Close the yaml file      
yamlfile.close()      

# Finish by counting how many remaining files exist in the data directory
numfiles = len([name for name in os.listdir(data_dir)])
log.write(' Number of files remaining in the Data directory - %s \n' % numfiles )


log.write('\n')
log.write('\n')
# --Close log file
log.close()
