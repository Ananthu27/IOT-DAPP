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

########## USER DEFINED CLASS IMPORTS
from message import Message
from device import Device

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

########## CREATING OBJECTS HERE
device_object = Device(device_name,port,master_key,master=master,future_master=True)
message_object = Message()


########## THIS IS THE MAIN FRAME

# if this device is a master device
if device_object.master:
    
    if new_group:
        new_group_created = device_object.createNewGroup()
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
            s.bind(('', port))
            print ('MASTER RUNNING AT %s:%s'%(host,str(port)))
            while True:
                # message , address = s.recvfrom(1024)
                # message = message.decode()
                # print ('recevied :',message,address)
                # ########### ANSWER DIFFERNET MESSAGES HERE
                # s.sendto(('echo recived : '+message).encode(),address)

                # getting incoming message and message number
                msg, address = s.recvfrom(1024)
                msg = message_object.getMessage(msg)
                print (msg)
                message_no = msg['message_no']
                
                # ########### ANSWER DIFFERNET MESSAGES HERE
                
                # ########### PUBLIC KEY EXCHANGE MESSAGES HANDLED HERE, MESSAGE NUMBER = 0
                if message_no == '0':
                    print ('here')
                    nonce = msg['nonce']
                    # with open((config['data_path']+'DeviceSpecific/Temp/%s_public_key')%(str(address[1])),'w') as f:
                    #     f.write(msg['public_key_serialised'])
                    print (msg)
                    response_msg = message_object.getPublicKeyMessage(device_object,to_port=address[1],nonce=nonce) 
                    s.sendto(response_msg,address)
        
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
        new_device_created = device_object.createNewDevice()
        if not new_device_created:
            print ('DEVICE ALREADY EXSIT ... EXITING')
            exit()

    if not isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt'):
        print ('IMPORTATN FILES ARE MISSING ... EXITING')
        exit()        

    # continue with while loop here
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(('', port))
            print ('DEVICE RUNNING AT %s:%s'%(host,str(port)))
            while True:
                # s.sendto('test message from client 2222'.encode(),(private_ip, 1111))
                # message, address = s.recvfrom(1024)
                # print('server replied with :', message, address)
                # s.close()
                # break

                if new_device:
                    msg = message_object.getPublicKeyMessage(device_object,to_port='1111',nonce=None)
                    s.sendto(msg,(public_ip,1111))
                    msg , address = s.recvfrom(1024)
                    msg = message_object.getMessage(msg)
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