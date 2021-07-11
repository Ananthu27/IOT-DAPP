########## HERE BLOCKCHAIN DEFAULT ACCOUNT IS SET BASED ON SUBSCRIBER

########## GENERAL IMPORTS
import json
from os.path import isfile

########## USER DEFINED FUNCTION IMPORTS
from network import getPorts, getPublicPirvateIp
from loopFollower import follower as followerLoop
from loopMaster import master as masterLoop

########## USER DEFINED CLASS IMPORTS
from message import Message
from device import Device

########## LOADING CONFIGURATION HERE
config = None
with open('config.json') as f:
    config = json.load(f)

########## INPUT FOR SERVER 
private_ip, public_ip = getPublicPirvateIp()
device_config = {

    # general details
    'host' : '127.0.0.1',
    'device_name' : 'Master1',
    'master_key' : 'Em0C2Kv9pM',
    'private_ip' : private_ip,
    'public_ip' : public_ip,
    'master_port' : None,
    'replace' : True,

    # master details 
    'master' : True,
    'new_group' : True,

    # follower details 
    'new_device' : False,
    'future_master' : False,
    'association' : False

}

if device_config['replace']:
    with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','w') as f:
        json.dump(device_config,fp=f,indent=5)

elif not isfile(config['data_path']+'DeviceSpecific/Device_data/device_config.json'):
    with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','w') as f:
        json.dump(device_config,fp=f,indent=5)

else :
    with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','r') as f:
        device_config = json.load(f)

########## ESTABLISHING PORT FOR SERVER HERE
port_list = getPorts()
port = None
for i in range (6*10**4,6*10**4+2**12,2):
    if str(i) not in port_list:
        port = i
        if device_config['master']:
            device_config['master_port'] = port
        break

########## CREATING OBJECTS HERE
device_object = Device(
    device_name=device_config['device_name'],
    port=port,
    master_key=device_config['master_key'],
    master=device_config['master'],
    future_master=device_config['future_master']
)
message_object = Message()

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO

server_logger = createLogger(name='Server',level=INFO,state='DEVELOPMENT')

########## THIS IS THE MAIN FRAME

########## MASTER DEVICE
if device_object.master:
    
    if device_config['new_group']:
        server_logger.info('\nATTEMPTING TO CREATE NEW GROUP')
        new_group_created = device_object.createNewGroup()
        # if new group cannot be created
        if not new_group_created:
            server_logger.info('\nGROUP ALREAD EXIST ... EXITING')
            exit()
        else :
            # update device config
            device_config['new_group'] = False
            with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','w') as f:
                json.dump(device_config,fp=f,indent=5)
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

########## FOLLOWER DEVICE
else:
    # check add device here
    if device_config['new_device']:
        server_logger.info('\nCREATING A NEW DEVICE')
        new_device_created = device_object.createNewDevice()
        if not new_device_created:
            server_logger.info('\nDEVICE ALREADY EXSIT ... EXITING')
            exit()
        else :
            device_config['new_device'] = False
            with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','w') as f:
                json.dump(device_config,fp=f,indent=5)

    if not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt'):
        server_logger.info('\nIMPORTATN FILES ARE MISSING ... EXITING')
        exit()        

    # continue with while loop here
    followerLoop(device_object,port,server_logger)