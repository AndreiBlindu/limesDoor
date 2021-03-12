'''
Created on 06 September 2018

@author: Andrei Blindu
Python Version: 3 
'''

# This script has to run in cron mode every tot minutes and updates the database with the authorized users that gets from Drupal

import requests, json
import sqlite3
from sqlite3 import Error
import configuration as conf

drupalURL = conf.drupalURL

#Connect to database (and eventually creates it if doesn't exist yet)
conn = sqlite3.connect(conf.database_path, check_same_thread=False)
#Make the cursor  
c = conn.cursor() 

try:
    #Create table if doesn't already exist
    c.execute('''CREATE TABLE utenti (username string, fingerprint string, start_period int, end_period int)''') 

except Error as err:
    print(err) #If table already exists prints the error and keeps working

    #If table already exists deletes the old list of authorized users in order to upload the new one without repetitions
    c.execute("DELETE FROM utenti")

#########################################################################################################
# GET AUTHORIZED USERS LIST FROM DRUPAL 

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

headers = {'Content-Type': 'application/json', 'X-CSRF-Token' : token, 'Cookie' : session_name + "=" + sessid}
#Gets view name from database
c.execute('SELECT * FROM door_info')
c.fetchone()
view_name = c.fetchone()[1]

#Get authorized users list as json
r = requests.get(str(drupalURL)+'/door_info/views/'+str(view_name)+'.json?display_id=services_1', headers=headers) 

#############################################################################################################

#Insert authorized users into the utenti table in the database
i=0
numero_utenti = len(r.json())
while i<numero_utenti:
    
    username = r.json()[i]['nome']
    fingerprint = r.json()[i]['fingerprint']
    periodo = r.json()[i]['start_date']
    
    inizio_periodo, fine_periodo = periodo.split(' to ')
    inizio = int(inizio_periodo)
    fine = int(fine_periodo)
    print('Inizio periodo : ',inizio)
    print('Fine periodo : ',fine)
    
    if fingerprint != None:
        c.execute('INSERT INTO utenti VALUES(?,?,?,?)', (username, fingerprint, inizio, fine))
        conn.commit() #Essential to save data, otherwise every time I run the script the database is empty
    
    i=i+1

#Does a print in order to verify that data has been inserted into the database correctly    
#c.execute("SELECT * FROM utenti") 
#print(c.fetchall())
#conn.close()