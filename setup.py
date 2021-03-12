'''
Created on 06 September 2018

@author: Andrei Blindu
Python Version: 3
'''

# This script compiles the table door_info with the machine view name got from Drupal according to the value of door nid

import requests, json
import sqlite3
from sqlite3 import Error
import os
import configuration as conf

try:
    #Imports pyfingerprint if exists
   from pyfingerprint.pyfingerprint import PyFingerprint 
except Error as err:
   print(err)
   #Otherwise installs it running .sh file if this package is missing
   os.system('bash '+str(conf.fipri_install_sh_path))

drupalURL = conf.drupalURL

#Connect to database (and eventually creates it if doesn't exist yet)
conn = sqlite3.connect(conf.database_path, check_same_thread=False)
#Make the cursor  
c = conn.cursor() 

# Gets door nid value from table door_info in database
c.execute('SELECT * FROM door_info ')
nid = c.fetchone()[0]

#########################################################################################################
# GET view name FROM DRUPAL

headers = {'Content-Type': 'application/json'}
#Obtain token
t = requests.post(str(drupalURL)+'/door_info/user/token.json', headers=headers) 
token = t.json()['token']
print('Token : ',token)

#Login
headers = {'Content-Type': 'application/json', 'X-CSRF-Token' : token}
#Gets username and password for authentication from the database
c.execute('SELECT * FROM door_info')
username = c.fetchone()[3]
password = c.fetchone()[4]
data = {"username" : username, "password" : password}
#Login with token and user credentials
l = requests.post(str(drupalURL)+'/door_info/user/login.json', headers=headers, json=data) 
sessid = l.json()['sessid']
token = l.json()['token'] #Gets new token
session_name = l.json()['session_name']
print('SessID : ',sessid)
print('Token : ',token)

#Get json with view machine name
headers = {'Content-Type': 'application/json', 'X-CSRF-Token' : token, 'Cookie' : session_name + "=" + sessid}
r = requests.get(str(drupalURL)+'/door_info/node/'+str(nid)+'.json', headers=headers)
nid = r.json()['nid']
view_name = r.json()['field_view_machine_name']['und'][0]['value']

##########################################################################################################

nid_hub = conf.nid_hub # Get nid_hub value from configuration file

# INSERT nid view_name and nid_hub INTO THE door_info TABLE IN THE DATABASE
c.execute('INSERT INTO door_info VALUES(?,?,?)', (nid, view_name, nid_hub, username, password))
conn.commit()