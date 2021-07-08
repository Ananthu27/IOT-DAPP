########## HERE BLOCKCHAIN DEFAULT ACCOUNT IS SET BASED ON SUBSCRIBER

########## GENERAL IMPORTS
import json
from os.path import isfile

########## USER DEFINED FUNCTION IMPORTS
from network import getPorts, getPublicPirvateIp

########## USER DEFINED CLASS IMPORTS
from message import Message
from device import Device
from loopFollower import follower as followerLoop
from loopMaster import master as masterLoop

########## INPUT FOR SERVER 
host = '127.0.0.1'
master = True
new_group = True
new_device = True
future_master = True
master_key = 'Em0C2Kv9pM'
device_name = 'testMaster'
private_ip, public_ip = getPublicPirvateIp()

########## LOADING CONFIGURATION HERE
config = None
with open('config.json') as f:
    config = json.load(f)

########## ESTABLISHING PORT FOR SERVER HERE
port_list = getPorts()
if '1111' not in port_list and master:
    port = 1111    
else :
    port = None
    for i in range (6*10**4,6*10**4+2**12,2):
        if str(i) not in port_list:
            port = i
            break

########## CREATING OBJECTS HERE
device_object = Device(device_name,port,master_key,master=master,future_master=True)
message_object = Message()

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO

server_logger = createLogger(name='Server',level=INFO,state='DEVELOPMENT')

########## THIS IS THE MAIN FRAME

# if this device is a master device
if device_object.master:
    
    if new_group:
        server_logger.info('\nATTEMPTING TO CREATE NEW GROUP')
        new_group_created = device_object.createNewGroup()
        # if new group cannot be created
        if not new_group_created:
            server_logger.info('\nGROUP ALREAD EXIST ... EXITING')
            exit()
        else :
            server_logger.info('\nNEW GROUP CREATION COMPLETE')


    # check if relevant files for master is available
    if (
        not isfile(config['data_path']+'DeviceSpecific/Device_data/group_table.json') 
        or not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt')
    ):
        server_logger.info('\nIMPORTATN FILES ARE MISSING ... EXITING')
        exit()
    else :
        server_logger.info('\nSETTING UP SERVER NOW')

    # continue infinite while loop
    masterLoop(device_object,port,server_logger)

# if device is not master
else:
    # check add device here
    if new_device:
        server_logger.info('\nCREATING A NEW DEVICE')
        new_device_created = device_object.createNewDevice()
        if not new_device_created:
            server_logger.info('\nDEVICE ALREADY EXSIT ... EXITING')
            exit()

    if not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt'):
        server_logger.info('\nIMPORTATN FILES ARE MISSING ... EXITING')
        exit()        

    # continue with while loop here
    followerLoop(device_object,port,server_logger,new_device)