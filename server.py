########## HERE BLOCKCHAIN DEFAULT ACCOUNT IS SET BASED ON SUBSCRIBER

########## GENERAL IMPORTS
from posix import listdir
import socket 
import traceback
import json
from web3 import Web3
from os.path import isfile

########## USER DEFINED FUNCTION IMPORTS
from network import getPorts, getPublicPirvateIp
from crypto import retrieveKeyPairRsa
from blockChain import getAbiAndBytecode
from device_functions import storeMyDevice
from device_functions import getPublicKeyMessage, getMessage
from contract_functions import createNewGroup, createNewDevice

########## INPUT FOR SERVER 
host = '127.0.0.1'
master = True
new_group = True
new_device = True
future_master = False
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

########## WRITING NEW DEVICE DATA HERE
storeMyDevice(port,device_name)

########## SETTING UP CONNECTION TO BLOCKCHAIN
ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[int(config['default_subsciber_accout'])]
abi, discard = getAbiAndBytecode(config['main_contract_path'])
contract = bcc.eth.contract(address=config['address'],abi=abi)

########## LOADING KEYS HERE
private_key_serialized, public_key_serialized = retrieveKeyPairRsa(master_key,serialize=True)

########## THIS IS THE MAIN FRAME
# if this device is a master device
if master:
    
    if new_group:
        new_group_created = createNewGroup(master_key,public_key_serialized)
        # if new group cannot be created
        if not new_group_created:
            print ('GROUP ALREAD EXIST ... EXITING')
            exit()

    # check if relevant files for master is available
    if (
        not isfile(config['data_path']+'DeviceSpecific/Device_data/group_table.json') 
        or not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt')
    ):
        print ('IMPORTATN FILES ARE MISSING ... EXITING')
        exit()

    # continue infinite while loop
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((host, port))
            print ('MASTER RUNNING AT %s:%s'%(host,str(port)))
            while True:

                # getting incoming message and message number
                msg, address = s.recvfrom(1024)
                msg = getMessage(msg)
                message_no = msg['message_no']
                
                ########### ANSWER DIFFERNET MESSAGES HERE
                
                ########### PUBLIC KEY EXCHANGE MESSAGES HANDLED HERE, MESSAGE NUMBER = 0
                if message_no == 0:
                    nonce = msg['nonce']
                    # with open((config['data_path']+'DeviceSpecific/Temp/%s_public_key')%(str(address[1])),'w') as f:
                    #     f.write(msg['public_key_serialised'])
                    print (msg)
                    print ()
                    print (address)
                    response_msg = getPublicKeyMessage(master_key=master_key,nonce=nonce)
                    s.sendto(msg,address)
        
        except OSError:
            print ('Port :',port,'taken')
        
        except KeyboardInterrupt:
            print('-- EXITING ON : KeyboardInterrupt --')
            s.close()

        except :
            traceback.print_exc()
        
        finally:
            s.close()

# if device is not master
else:
    # check add device here
    if new_device:
        new_device_created = createNewDevice(master_key,public_key_serialized,host,future_master)
        if not new_device_created:
            print ('DEVICE ALREADY EXSIT ... EXITING')
            exit()

    if not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt'):
        print ('IMPORTATN FILES ARE MISSING ... EXITING')
        exit()        

    # continue with while loop here
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((host, port))
            print ('DEVICE RUNNING AT %s:%s'%(host,str(port)))
            while True:
                if new_device:
                    msg = getPublicKeyMessage(master_key,to_port='1111',nonce=None)
                    s.sendto(msg,(public_ip,1111))
                    msg , address = s.recvfrom(1024)
                    msg = getMessage(msg)
                    # verify last nonce here
                    print(msg,address)
                    # continue with association request
                    new_device = False
        
        except OSError:
            print ('Port :',port,'taken')

        except KeyboardInterrupt:
            print('-- EXITING ON : KeyboardInterrupt --')
            s.close()
        
        except :
            traceback.print_exc()
        
        finally:
            s.close()