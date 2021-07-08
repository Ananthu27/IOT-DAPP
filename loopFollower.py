######## GENERAL IMPORTS
from logging import Logger
import socket 
import traceback
import json

######## USERDEFIED FUNCTIONS/CLASSES/OBJECTS IMPORT
from message import Message
from network import getPublicPirvateIp
from crypto import decryptRSA, loadKeyPairRSA

message_object = Message()
host = ''
private_ip, public_ip = getPublicPirvateIp()

########## LOADING CONFIGURATION HERE
config = None
with open('config.json') as f:
    config = json.load(f)

def follower(device_object,port,logger):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind(('', port))
            logger.info('\nDEVICE RUNNING AT %s:%s'%(host,str(port)))

            while True:

                if new_device:

                    logger.info('\n')
                    logger.info('\nINITIATING PUBLIC KEY EXCHANGE WITH MASTER')
                    msg = message_object.getPublicKeyMessage(device_object,to_port='1111',nonce=None)
                    s.sendto(msg,(public_ip,1111))
                    msg , address = s.recvfrom(2**16)
                    msg = message_object.getMessage(msg)

                    # first check nonce of public key exchange
                    if device_object.last_nonce[str(1111)] == decryptRSA(device_object.private_key,msg['nonce']):

                        logger.info('\nPUBLIC KEY EXCHANGE WITH MASTER COMPLETE')
                        logger.info('\nINITIATING DEVICE ASSOCIATION REQUEST')

                        discard, to_public_key = loadKeyPairRSA(msg['public_key_serialized'],device_object.master_key)
                        association_msg = message_object.getAssociationRequestMssg(device_object,1111,to_public_key)
                        s.sendto(association_msg,(public_ip,1111))
                        association_resp_msg , address = s.recvfrom(2**16)
                        association_resp_msg = message_object.getMessage(association_resp_msg)
                        association_resp_msg['nonce'] = decryptRSA(device_object.private_key,association_resp_msg['nonce'])

                        if association_resp_msg['nonce'] == device_object.last_nonce[str(1111)] \
                        and device_object.verifyGroupCreation(association_resp_msg['group_creation_tx_receipt']):
                            logger.info('\nGROUPCREATION VERIFIED MASTER AUTHENTICATED')
                            group_table_df = association_resp_msg['group_table']
                            group_table_df.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
                            logger.info('\nGROUPTABLE UPDATED')
                        
                        else:
                            logger.info('\nSUSPECT MASTER',address)
                            logger.info('\nDEVICE ASSOSICATION INCOMPLETE')
                    
                    new_device = False

                #ping master
                #check outbox
                #check inbox (5second while)

        except socket.timeout:
            Logger.warning('FOLLOWER TIMEOUT.')
            s.close()
            follower(device_object,port,Logger)
        
        except KeyboardInterrupt:
            logger.info('\n-- EXITING ON : KeyboardInterrupt --')
            s.close()
        
        except :
            traceback.print_exc()
        
        finally:
            s.close()