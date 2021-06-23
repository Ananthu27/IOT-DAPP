########## HERE BLOCKCHAIN DEFAULT ACCOUNT IS SET BASED ON SUBSCRIBER

########## GENERAL IMPORTS
from pickle import NONE
from posix import listdir
import socket 
import traceback
import json
from web3 import Web3
from os.path import isfile

########## USER DEFINED FUNCTION IMPORTS
from network import getPorts, getPublicPirvateIp
from crypto import loadKeyPairRSA
from crypto import decryptRSA

########## USER DEFINED CLASS IMPORTS
from message import Message
from device import Device

########## INPUT FOR SERVER 
host = '127.0.0.1'
master = True
new_group = False
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
from logging import INFO, log
from functools import wraps

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
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(('', port))
            server_logger.info('\nMASTER RUNNING AT %s:%s'%(host,str(port)))
            while True:

                # getting incoming message and message number
                msg, address = s.recvfrom(1024)
                msg = message_object.getMessage(msg)
                message_no = msg['message_no']
                server_logger.info('\nMESSAGE NO : %s FROM (%s,%d)'%(message_no,address[0],address[1]))
                
                ########### ANSWER DIFFERNET MESSAGES HERE
                
                ########### PUBLIC KEY EXCHANGE MESSAGES HANDLED HERE, MESSAGE NUMBER = 0 (RESPONSE)
                if message_no == '0':
                    server_logger.info('\n')
                    server_logger.info('\nPUBLIC KEY EXCHANGE BEGIN WITH (%s,%d)'%(address[0],address[1]))
                    nonce = msg['nonce']
                    discard, to_public_key = loadKeyPairRSA(msg['public_key_serialized'],device_object.master_key)
                    response_msg = message_object.getPublicKeyMessage(device_object,to_port=None,nonce=nonce,to_public_key=to_public_key) 
                    s.sendto(response_msg,address)
                    server_logger.info('\nPUBLIC KEY EXCHANGE COMPLETE WITH (%s,%d)'%(address[0],address[1]))

                ########### INCOMING ASSOCIATION REQUEST HANDLED HERE, MESSAGE NUMBER = 1 (RESPONSE)
                elif message_no == '1':
                    server_logger.info('\n')
                    server_logger.info('\nASSOCIATION REQUEST FROM (%s,%d)'%(address[0],address[1]))
                    association_msg = msg
                    nonce = decryptRSA(device_object.private_key,association_msg['nonce'])
                    discard, to_public_key = loadKeyPairRSA(association_msg['public_key_serialized'],device_object.master_key)
                    # if device is authenticated 
                    if device_object.verifyDeviceAssociation(association_msg['association_tx_receipt']):
                        server_logger.info('\nVERIFIED DEVICE ASSOCIATION FOR (%s,%d)'%(address[0],address[1]))
                        # add to group table here
                        device_object.addDeviceToGroupTable(
                            '%s::%s'%(private_ip,public_ip),
                            address[1],
                            association_msg['device_name'],
                            association_msg['public_key_serialized'],
                            association_msg['future-master']
                        )
                        server_logger.info('\nADDED (%s,%d) TO GROUPTABLE'%(address[0],address[1]))
                        response_msg = message_object.getAssociationResponseMssg(device_object,nonce,to_public_key)
                        enc_reponse_msg = response_msg
                        s.sendto(enc_reponse_msg,address)
                        server_logger.info('\nASSOCIATION RESPONSE SENT TO (%s,%d)'%(address[0],address[1]))
                        server_logger.warn('\nASSOCIATION REQUEST COMPLETE WITH (%s,%d)'%(address[0],address[1]))
                    else:
                        server_logger.warn('\nSUSPECT (%s,%d)'%(address[0],address[1]))
                        server_logger.warn('\nASSOCIATION REQUEST INCOMPLETE WITH (%s,%d)'%(address[0],address[1]))
        
        except OSError:
            server_logger.info('\nPort : %d taken'%(port))
        
        except KeyboardInterrupt:
            server_logger.info('\n-- EXITING ON : KeyboardInterrupt --')
            s.close()

        except :
            traceback.print_exc()
        
        finally:
            s.close()

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
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(('', port))
            server_logger.info('\nDEVICE RUNNING AT %s:%s'%(host,str(port)))

            while True:
                if new_device:
                    server_logger.info('\n')
                    server_logger.info('\nINITIATING PUBLIC KEY EXCHANGE WITH MASTER')
                    msg = message_object.getPublicKeyMessage(device_object,to_port='1111',nonce=None)
                    s.sendto(msg,(public_ip,1111))
                    msg , address = s.recvfrom(1024)
                    msg = message_object.getMessage(msg)

                    # first check nonce of public key exchange
                    if device_object.last_nonce[str(1111)] == decryptRSA(device_object.private_key,msg['nonce']):
                        server_logger.info('\nPUBLIC KEY EXCHANGE WITH MASTER COMPLETE')
                        server_logger.info('\nINITIATING DEVICE ASSOCIATION REQUEST')
                        discard, to_public_key = loadKeyPairRSA(msg['public_key_serialized'],device_object.master_key)
                        association_msg = message_object.getAssociationRequestMssg(device_object,1111,to_public_key)
                        s.sendto(association_msg,(public_ip,1111))

                        association_resp_msg , address = s.recvfrom(1024)
                        association_resp_msg = message_object.getMessage(association_resp_msg)
                        association_resp_msg['nonce'] = decryptRSA(device_object.private_key,association_resp_msg['nonce'])

                        if association_resp_msg['nonce'] == device_object.last_nonce(str(1111)) \
                        and device_object.verifyGroupCreation(association_resp_msg['group_creation_tx_receipt']):
                            server_logger.info('\nGROUPCREATION VERIFIED MASTER AUTHENTICATED')
                            group_table_df = association_resp_msg['group_table']
                            group_table_df.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
                            server_logger.info('\nGROUPTABLE UPDATED')
                        else:
                            server_logger.info('\nSUSPECT MASTER',address)
                            server_logger.info('\nDEVICE ASSOSICATION INCOMPLETE')

                    new_device = False
        
        except OSError:
            server_logger.info('\nPort : %d taken'%(port))

        except KeyboardInterrupt:
            server_logger.info('\n-- EXITING ON : KeyboardInterrupt --')
            s.close()
        
        except :
            traceback.print_exc()
        
        finally:
            s.close()