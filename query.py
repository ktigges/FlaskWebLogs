# Date:     06/20/2026  
# Updated:  07/05 - Modified form and updated query logic
# Version:  0.2
#
# query.py - Imported into main logic script - not stand alone
#
import requests
# Uncomment pdb to set debug trace
import pdb
from cryptography.fernet import Fernet
import os
import time
import base64
import os
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
import xml.etree.ElementTree as ET
import sys


def get_options():
    cwd = './'
    #option 1 = panorama_ip
    #option 2 = ssl_enable
    #cwd = '/Users/ktigges/dev/logs-web/'
    panorama_ip = ''
    ssl_enable = ''
    port = ''
    with open(cwd + 'config.options', 'r') as f:
        contents = (f.readline())
        x = 12
        while (contents[x] != '\n'):
           panorama_ip = panorama_ip + contents[x]
           x = x + 1
        
    f.close()    
    return(panorama_ip)        
            
            


def get_api():
# Password is encrypted so it is not present in this script and is read from 2 files containing the encrypted password and key
# There is a script called encryptpwd.py that should be used to generate the encrypted password to be used prior to using this script
#
# Place the password in a file called pwd.txt (This will be deleted once the encrypted password is generated)
# Run the script - python3 ./encryptpwd.py
# 2 files will be generated that should be kept in the script directory and will be utilized to authenticate below
#
# read encrypted pwd and convert into byte
#
    cwd = './'
    # cwd = '/Users/ktigges/dev/logs-web/'
    with open(cwd + 'apipass.txt') as f:
        apipwd = ''.join(f.readlines())
        encpwdbyt = bytes(apipwd, 'utf-8')
    f.close()

    # read key and convert into byte
    with open(cwd + 'apikey.txt') as f:
        refKey = ''.join(f.readlines())
        refKeybyt = bytes(refKey, 'utf-8')
    f.close()

    # use the key and decrypt the password

    keytouse = Fernet(refKeybyt)
    # Convert the password from byte to Ascii
    api_key = (keytouse.decrypt(encpwdbyt)).decode('ASCII')
    return api_key.strip()


def returnheader(api_key):
# Functions returns the "Authorization Basic" header with the userid:password encoded in base64
#
    #authstr = user_id + ":" + user_password
    #bytestr = authstr.encode('ascii')
    #authb64 = base64.b64encode(bytestr)
    #authb64 = str(authb64, encoding='utf-8')

    header = { 'X-PAN-KEY' : f'{api_key}'}
    return(header)


def getjobid(txtresponse):
# response will have the job ID after the <job> tag
# Loop through the response after the <job> tag until the end tag starts (</job>) grabbing out the job number
#
    i = txtresponse.find('<job>')
    # what position is the <job> string at?
    jobid = ""
    # Start at the position 5 over from the tag
    i = i + 5
    # while the incrementer is less than the total length
    while i < len(txtresponse):
        #if we have hit the end of job tag (<) then break out - we are done
        if (txtresponse[i] == "<"):
            break
        #otherwise add the jobid character to the end result
        else:
            jobid = jobid + txtresponse[i]
        #increment the counter
        i = i + 1
    return(jobid)

def query_logs(api_key, panorama_ip, source_ip, destination_ip, start_time, end_time, dport):
    # Build the API request URL
    
    query = f"receive_time geq '{start_time}' and receive_time leq '{end_time}'"

    if (source_ip):
        query += f" and src eq {source_ip}"
    if (destination_ip):
        query += f" and dst eq {destination_ip}"
    if (not dport == 'all'):
        query += f" and dport eq {dport}"
    
    url = f'https://{panorama_ip}/api/?type=log&log-type=traffic&nlogs=1000&query={query}'

    response = requests.post(url, headers = returnheader(api_key), verify=False)
    # Check the API response status as well as the code returned.  19 will be job enqueued, anything else we don't want to run as there is an error
    if (response.status_code == 200 and str(response.content).find('code="19"')) > 0:
        return(response)
    else:
        print(f'Error occurred. Status code: {response.status_code}, Response content: {response.content}')
    return(response)
   
def get_status(api_key, panorama_ip, jobid):
    status = 'ACT'
    while status == 'ACT':
       # While the status of the API call is ACT, wait 2 seconds and try again
       # Then when job is done, return the string to the calling program
        url =  f'https://{panorama_ip}/api/?type=log&log-type=traffic&action=get&job-id={jobid}'
        response = requests.get(url, headers = returnheader(api_key), verify=False)
        xml_string = str(response.content, 'utf-8')
        xml_string = xml_string.replace('\n', '')
        xml_string = response.content
        root = ET.fromstring(xml_string)
        element = root.findall('result/job')
        for job in element:
            status = job.find('status').text
            time.sleep(2)
    
    return(xml_string)



def main(panorama_ip, source_ip, destination_ip, start_time, end_time,  port):
    api_key = get_api()
    # panorama_ip = "192.168.254.5"

    # Set the query parameters

    # Get the start / end times based on minutes sent, and convert to string
    
    # start_time = end_time - timedelta(minutes = minutes)
    
    # start_time = start_time.strftime("%Y/%m/%d %H:%M:%S")
    # end_time = end_time.strftime("%Y/%m/%d %H:%M:%S")
 
    jobid = ""

    try:
     
       response = query_logs(api_key, panorama_ip, source_ip, destination_ip, start_time, end_time, port)
       jobid = getjobid(response.text)

       print('Query Queued : Job ID ' + jobid + '\n')
       xml_string = get_status(api_key, panorama_ip, jobid)
       return (xml_string)
       
    except Exception as e:
        print(f"Failed to query logs : {str(e)}")


    



