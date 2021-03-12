#Configuration file, contains all variables used
'''
Created on 06 September 2018

@author: Andrei Blindu
Python Version: 3
'''

import RPi.GPIO as GPIO

# URLs
# Complete url to Drupal controller
drupalUrl = 'https://limeslab.cleversoft.it'

# FILE PATHs
# Database path
database_path = '/root/door_info.db'
# Path of pyfingerprint .sh installation file
fipri_install_sh_path = 'pyfingerprint_install/pyfingerprint_install.sh'

# Id of the hub, default 1 (it will be set from console input by user together with nid in door_nid_config.py when we have more hubs)
hub_id = 1

# Default values for python scripts
apertura = False
memory_update = False

# Values of GPIO pins
pin_relay = 17




