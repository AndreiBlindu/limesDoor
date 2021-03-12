'''
Created on 06 September 2018

@author: Andrei Blindu
Python Version: 3
'''

# This script creates the database and the table door_info in it, then gets the nid of the door
# from the user through console input and insert it into the table

import requests, json
import sqlite3
from sqlite3 import Error
import configuration as conf

#Connect to database (and eventually creates it if doesn't exist yet)
conn = sqlite3.connect(conf.database_path, check_same_thread=False)
#Make the cursor  
c = conn.cursor() 

try:
    #Create table if doesn't already exist
    c.execute('''CREATE TABLE door_info (nid int, view_name string, nid_hub int, username string, password string)''') 

except Error as err:
    print(err)

    #If table exists deletes items from it in order to upload new ones
    c.execute("DELETE FROM door_info")

# Gets nid from console input and hub_id from the configuration file
nid = int(input("Nid = ")) 
hub_id = conf.hub_id
# Here we set the username and password we use for authentication when we send requests to Drupal
username = str(input("Username : "))
password = str(input("Password : "))

# Insert nid, hub_id, username and password into the table door_info in the database    
c.execute('INSERT INTO door_info VALUES(?,?,?,?,?)', (nid, "", hub_id, username, password))
conn.commit()