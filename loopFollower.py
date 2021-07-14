######## GENERAL IMPORTS
from datetime import datetime
from loopMaster import master
import socket 
import traceback
import json
from os import listdir
from os.path import isfile
from os import rename
from time import sleep
import pickle

######## USERDEFIED FUNCTIONS/CLASSES/OBJECTS IMPORT
from message import Message
from network import getPublicPirvateIp
from crypto import decryptRSA, loadKeyPairRSA
from random import choice

message_object = Message()
host = ''
private_ip, public_ip = getPublicPirvateIp()
ping_attempt = 0

########## LOADING CONFIGURATION HERE
config = None
with open('config.json') as f:
    config = json.load(f)

def follower(device_object,port,logger):

    ######### LOADING DEVICE CONFIG HERE
    device_config = None
    if isfile(config['data_path']+'DeviceSpecific/Device_data/device_config.json'):
        with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','r') as f:
            device_config = json.load(f)
    global ping_attempt

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.settimeout(30)
            s.bind(('', port))
            logger.info('\nDEVICE RUNNING AT %s:%s'%(host,str(port)))

        
            ######## CREATION OF NEW DEVICE HERE
            if not device_config['association']:

                logger.info('\n')
                logger.info('\nINITIATING PUBLIC KEY EXCHANGE WITH MASTER')
                msg = message_object.getPublicKeyMessage(device_object,to_port=device_config['master_port'],nonce=None)
                s.sendto(msg,(public_ip,device_config['master_port']))
                logger.info('\nWAITING FOR PUBLIC KEY EXCHANGE REPLY (EXITING IN 30S)')
                msg , address = s.recvfrom(2**16)
                msg = message_object.getMessage(msg)

                # first check nonce of public key exchange
                if device_object.last_nonce[str(device_config['master_port'])] == decryptRSA(device_object.private_key,msg['nonce']):
                    logger.info('\nPUBLIC KEY EXCHANGE WITH MASTER COMPLETE')
                    logger.info('\nINITIATING DEVICE ASSOCIATION REQUEST')

                    discard, to_public_key = loadKeyPairRSA(msg['public_key_serialized'],device_object.master_key)
                    association_msg = message_object.getAssociationRequestMssg(device_object,device_config['master_port'],to_public_key)
                    s.sendto(association_msg,(public_ip,device_config['master_port']))
                    logger.info('\nWAITING FOR ASSOCIATION RESPONSE (EXITING IN 30S)')
                    association_resp_msg , address = s.recvfrom(2**16)
                    association_resp_msg = message_object.getMessage(association_resp_msg)
                    association_resp_msg['nonce'] = decryptRSA(device_object.private_key,association_resp_msg['nonce'])

                    if association_resp_msg['nonce'] == device_object.last_nonce[str(device_config['master_port'])] \
                    and device_object.verifyGroupCreation(association_resp_msg['group_creation_tx_receipt']):
                        logger.info('\nGROUPCREATION VERIFIED MASTER AUTHENTICATED')
                        group_table_df = association_resp_msg['group_table']
                        group_table_df.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
                        with open(config['data_path']+'DeviceSpecific/Device_data/group_table','wb') as f:
                            pickle.dump(group_table_df,f)
                        with open(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt','wb') as f:
                            pickle.dump(association_resp_msg['group_creation_tx_receipt'],f)
                        # updating device config
                        device_config['association'] = True
                        with open(config['data_path']+'DeviceSpecific/Device_data/device_config.json','w') as f:
                            json.dump(device_config,fp=f,indent=5)
                        logger.info('\nGROUPTABLE UPDATED')
                        
                    else:
                        logger.info('\nSUSPECT MASTER (%s,%d)'%(address[0],address[1]))
                        logger.info('\nDEVICE ASSOSICATION INCOMPLETE')
                        sleep(5)
                        s.close()
                        follower(device_object,port,logger)
                    
            ######## PING MASTER HERE
            group_table_df = device_object.retrieveGroupTable()
            master_device = (group_table_df.loc[group_table_df['MPRECIDENCE']==0]).iloc[0]
            
            last_master_ping = (datetime.now()-(datetime.strptime(master_device['LAST_PING'],'%Y-%m-%d %H:%M:%S')))
            last_master_ping = last_master_ping.total_seconds()
            discard, to_public_key = loadKeyPairRSA(master_device['PUB_KEY'],device_object.master_key)
            
            if last_master_ping > 300:
                ping_msg = message_object.getPingMessage(
                    device_object,
                    master_device['PORT'],
                    to_public_key
                )
                s.sendto(ping_msg,(public_ip,int(master_device['PORT'])))
                ping_attempt += 1
                logger.info('\nPING MESSAGE SENT TO MASTER\nATTEMPT :%d'%(ping_attempt))
                sleep(10)

            ######## CHECKING OUPBOX HERE
            temp = listdir(config['data_path']+'DeviceSpecific/Outbox')
            if len(temp):
                outbox = []
                for item in temp:
                    if item.endswith('.pending.json'):
                        outbox.append(item)

                if len(outbox):
                    for messageName in outbox:
                        device_object.addMessage(config['data_path']+'DeviceSpecific/Outbox/'+messageName)
                    del outbox

                temp = listdir(config['data_path']+'DeviceSpecific/Outbox')
                ping = []
                for item in temp:
                    if item.endswith('.pending.ping.json'):
                        ping.append(item)
                
                if len(ping):
                    # ping a random transaction, sleep and exit
                    messageName = config['data_path']+'DeviceSpecific/Outbox/'+choice(ping)
                    msg_info = None
                    tx_receipt = None
                    with open(messageName,'r') as f:
                        msg_info = json.load(f)
                    with open(msg_info['tx_receipt'],'rb') as f:
                        tx_receipt = pickle.load(f)
                    msg = message_object.getMessageTransactionPingMssg(
                        device_object,
                        tx_receipt,
                        msg_info['message_id']
                    )
                    s.sendto(msg,(public_ip,int(msg_info['port'])))

                    if device_config['master_port']:
                        if (int(msg_info['port'])==device_config['master_port']):
                            sleep(5)
                    
                    # send audit trail to master 
                    audit_msg = message_object.getAuditMssg(
                        device_object,
                        msg_info['message_id'],
                        msg_info['to_device_name'],
                        subject='Data Message Transaction with message_id = %s Completed!'%(msg_info['message_id'])
                    )
                    s.sendto(audit_msg,(public_ip,device_config['master_port']))
                    logger.info('\n AUDIT TRAIL MESSAGE SENT TO SERVER.')

                    rename(messageName,messageName.replace('.pending.ping','.completed'))

            ######## LOOP FOR INCOMING MESSAGES UNTIL TIMEOUT
            logger.info('\nWAITING FOR INCOMMING MESSAGES (EXITING IN 30S)')
            msg, address = s.recvfrom(2**16)
            msg = message_object.getMessage(msg)
            message_no = msg['message_no']
            logger.info('\nMESSAGE NO : %s FROM (%s,%d)'%(message_no,address[0],address[1]))

            ######## ANSWER DIFFERNET MESSAGES HERE
            
            ######## ALIVE PING RESPONSE HANDLED HERE
            if message_no=='4':
                # verify nonce
                if device_object.last_nonce[str(device_config['master_port'])] == \
                    decryptRSA(device_object.private_key,msg['nonce']) :
                    # update grouptable 
                    group_table_df = device_object.retrieveGroupTable()
                    master_device = (group_table_df.loc[group_table_df['MPRECIDENCE']==0]).iloc[0]
                    device_object.updateLastPing(
                        master_device.name
                    )
                    ping_attempt = 0
                    logger.info('\nPING RESPONSE FROM MASTER\nMASTER LAST PING UPDATED')

            ######## DATA_MSG TRANACTION PING MESSAGE HANDLED HERE, MESSAGE NUMBER = 5
            elif message_no == '5':
                if device_object.verifyMessageTransaction(msg['message_tx_eceipt']):
                    device_object.getMessage(msg,address[1])

            ######## UNIDENTIFIED MESSAGE NO
            else :
                logger.warning('UNIDENTIFIED MESSAGE NO : %s'%(message_no))

            ######## FINALLY LOOP AGAIN
            s.close()
            follower(device_object,port,logger)

        except socket.timeout:
            logger.warning('FOLLOWER TIMEOUT.')
            s.close()
            follower(device_object,port,logger)
        
        except KeyboardInterrupt:
            logger.info('\n-- EXITING ON : KeyboardInterrupt --')
            s.close()
        
        except :
            traceback.print_exc()
        
        finally:
            s.close()