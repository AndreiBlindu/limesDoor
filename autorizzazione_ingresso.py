'''
Created on 06 September 2018

@author: Andrei Blindu
Python Version: 3
'''

import sqlite3
import time
import hashlib
import os
import RPi.GPIO as GPIO
import configuration as conf
from pyfingerprint.pyfingerprint import PyFingerprint 

# VARIABLES FROM CONFIGURATION FILE
memory_update = conf.memory_update
apertura = conf.apertura
pin = conf.pin_relay
database_path = conf.database_path

# GPIO CONFIGURATION
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)

# CODE TO ACTIVATE RELAY AND OPEN THE DOOR
def ApriPorta():
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pin, GPIO.LOW)
    return False #apertura must be set back on False

# Code to delete old templates and get updated ones from the database if the user is not recognized
def del_and_updateTemplates(f, dbcursor):
    # Deletes all templates
    n_templates = f.getTemplateCount()
    pos=0
    while pos<n_templates:
        if(f.deleteTemplate(pos)):
            print("Template deleted")
            pos=pos+1

    # Updates new templates from database        
    dbcursor.execute("SELECT * FROM utenti")
    users = dbcursor.fetchall()
    
    a=0
    while a<len(users):
        fingerprint = users[a][1] 
        characterics = list(map(int, fingerprint.split(' , '))) #Reconvert string into array of integers
        f.uploadCharacteristics(0x01, characterics)             #because uploadCharacteristics needs integers as argument
        f.storeTemplate(a, 0x01)
        a=a+1

    return False #memory_update must be set to false after this

def initializePyfingerprint():
    try:
        f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0X00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')
        else:
            return f
    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: '+str(e))

# Code to verify if the user is authorized
def verifyUser(user):
    if user==None: #If user's fingerprint is not in the database the access is denied otherwise the user is recognized and authorized
        print('Accesso negato')
        return False
    else:  #Verify if the user is authorized in this period
        now = int(time.time())
        start_period = int(user[2])
        end_period = int(user[3])

        if (now>start_period and now<end_period):
            print('Accesso autorizzato')
            print('Benvenuto ', user[0]) #Print username
            return True
        else:
            print("Utente non autorizzato in questo periodo")
            return False

def readFingerprint():
    #Connect to database (and eventually creates it if doesn't exist yet)
    conn = sqlite3.connect(database_path, check_same_thread=False)
    #Make the cursor
    c = conn.cursor()

    while True:
        f = initializePyfingerprint()

        if memory_update:
            memory_update = del_and_updateTemplates(f, c)

        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        try:
            print('Waiting for finger...')
            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Searchs template
            result = f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]

            if ( positionNumber == -1 ):
                print('No match found!')
                impronta = ""
            else:
                print('Found template at position #' + str(positionNumber))
                print('The accuracy score is: ' + str(accuracyScore))
                apertura = True

            f.loadTemplate(positionNumber, 0x01)
            characterics = f.downloadCharacteristics(0x01) #Array of intergers
            impronta = ','.join(map(str, characterics)) #Join the array values into a string

            # Searchs user that match the fingerprint in the database
            c.execute("SELECT * FROM utenti WHERE fingerprint=?", (impronta,))
            user = c.fetchone()

            apertura = verifyUser(user)
            if apertura:
                apertura = ApriPorta() #apertura is set back to False

        except Exception as exc:
            print('Operation failed!')
            print('Exception message: '+str(exc))
            if str(exc) == 'The given position number is invalid!' :
                memory_update = True
                # This means that the user is not found in templates so they will be syncronized with the database
            user = None #Otherwise if no fingerprint is readen and for any reason the program bypass the image reading user remains the last user

if __name__ == '__main__':
    readFingerprint()
