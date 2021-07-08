######## GENERAL IMPORTS
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

def master(device_object,port,logger):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.settimeout(30)
            s.bind(('', port))
            logger.info('\nMASTER RUNNING AT %s:%s'%(host,str(port)))

            while True:
                # getting incoming message and message number
                msg, address = s.recvfrom(2**16)
                msg = message_object.getMessage(msg)
                message_no = msg['message_no']
                logger.info('\nMESSAGE NO : %s FROM (%s,%d)'%(message_no,address[0],address[1]))

                ########### ANSWER DIFFERNET MESSAGES HERE

                ########### PUBLIC KEY EXCHANGE MESSAGES HANDLED HERE, MESSAGE NUMBER = 0 (RESPONSE)
                if message_no == '0':
                    logger.info('\n')
                    logger.info('\nPUBLIC KEY EXCHANGE BEGIN WITH (%s,%d)'%(address[0],address[1]))
                    nonce = msg['nonce']
                    discard, to_public_key = loadKeyPairRSA(msg['public_key_serialized'],device_object.master_key)
                    response_msg = message_object.getPublicKeyMessage(device_object,to_port=None,nonce=nonce,to_public_key=to_public_key) 
                    s.sendto(response_msg,address)
                    logger.info('\nPUBLIC KEY EXCHANGE COMPLETE WITH (%s,%d)'%(address[0],address[1]))

                ########### INCOMING ASSOCIATION REQUEST HANDLED HERE, MESSAGE NUMBER = 1 (RESPONSE)
                elif message_no == '1':

                    logger.info('\n')
                    logger.info('\nASSOCIATION REQUEST FROM (%s,%d)'%(address[0],address[1]))
                    association_msg = msg
                    nonce = decryptRSA(device_object.private_key,association_msg['nonce'])
                    discard, to_public_key = loadKeyPairRSA(association_msg['public_key_serialized'],device_object.master_key)

                    # if device is authenticated 
                    if device_object.verifyDeviceAssociation(association_msg['association_tx_receipt']):
                        logger.info('\nVERIFIED DEVICE ASSOCIATION FOR (%s,%d)'%(address[0],address[1]))
                        # add to group table here
                        device_object.addDeviceToGroupTable(
                            '%s::%s'%(private_ip,public_ip),
                            address[1],
                            association_msg['device_name'],
                            association_msg['public_key_serialized'],
                            association_msg['future_master']
                        )
                        logger.info('\nADDED (%s,%d) TO GROUPTABLE'%(address[0],address[1]))
                        response_msg = message_object.getAssociationResponseMssg(device_object,nonce,to_public_key)
                        enc_reponse_msg = response_msg
                        s.sendto(enc_reponse_msg,address)
                        logger.info('\nASSOCIATION RESPONSE SENT TO (%s,%d)'%(address[0],address[1]))
                        logger.warning('\nASSOCIATION REQUEST COMPLETE WITH (%s,%d)'%(address[0],address[1]))

                    else:
                        logger.warning('\nSUSPECT (%s,%d)'%(address[0],address[1]))
                        logger.warning('\nASSOCIATION REQUEST INCOMPLETE WITH (%s,%d)'%(address[0],address[1]))

        except socket.timeout:
            logger.warning('\n SERVER TIMEOUT DUE TO INACTIVITY')
            s.close()
            master(device_object,port,logger)
            
        except KeyboardInterrupt:
            logger.info('\n-- EXITING ON : KeyboardInterrupt --')
            s.close()

        except :
            traceback.print_exc()

        finally:
            s.close()
