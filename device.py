from blockChain import logExceptionsWrapper
import pandas as pd
from network import getPublicPirvateIp
from datetime import datetime
from crypto import decryptRSA, encryptRSA, loadKeyPairRSA, retrieveKeyPairRsa
import json 
from os import listdir, rename
from os.path import isfile
import pickle
from crypto import retrieveKeyPairRsa
from random import random

config = None
with open('config.json','r') as f:
    config = json.load(f)

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO, log
from functools import wraps

device_logger = createLogger(name='Device',level=INFO,state='DEVELOPMENT')

from web3 import Web3
from blockChain import getAbiAndBytecode

config = None
with open('config.json') as f:
    config = json.load(f)
private_ip, public_ip = getPublicPirvateIp()


ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[int(config['default_subsciber_accout'])]
abi , disacrd = getAbiAndBytecode(config['main_contract_path'])
contract = bcc.eth.contract(address=config['address'],abi=abi)


class Device:

    ########## WRAPPER FOR LOGGER
    def logExceptionsWrapper(function):
        @wraps(function)
        def logExceptions(*args,**kwargs):
            try:
                return function(*args,**kwargs)
            except:
                print ('################# DEVICE ERROR ###############')
                device_logger.exception('exception in device_functions.py.%s'%(function.__name__))
                print ('exception in device_functions.py.%s'%(function.__name__))
                print ('################# DEVICE ERROR ###############')
        return logExceptions

    ########## CONSTRUCTOR
    @logExceptionsWrapper
    def __init__(self,device_name,port,master_key,master=False,future_master=False):
        self.device_name = device_name
        self.port = port 
        self.master_key = master_key
        self.master = master
        self.future_master = master if master else future_master
        self.private_key, self.public_key = retrieveKeyPairRsa(self.master_key)
        self.private_key_serialized, self.public_key_serialized = retrieveKeyPairRsa(self.master_key,serialize=True)
        self.last_nonce = {}

    ############################## FOLLOWING ARE FUNCTION ON LOCAL FILES ########################################

    ########## FUNCTION TO CREATE GROUP TABLE
    @logExceptionsWrapper
    def createGroupTable(self):
        if self.master :
            group_table = pd.DataFrame()
            # columns=['IP','PORT','DEVICE_NAME','PUB_KEY','TIMESTAMP','MPRECIDENCE','LAST_PING']
            private_ip, public_ip = getPublicPirvateIp()
            discard, public_key_serialized = retrieveKeyPairRsa(self.master_key,True)

            group_table['IP'] = [('%s/%s')%(private_ip,public_ip)]
            group_table['PORT'] = [self.port]
            group_table['DEVICE_NAME'] = [self.device_name]
            group_table['PUB_KEY'] = [public_key_serialized]
            group_table['TIMESTAMP'] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            group_table['MPRECIDENCE'] = [0]
            group_table['LAST_PING'] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]

            # storing group table
            with open(config['data_path']+'DeviceSpecific/Device_data/group_table','wb') as f:
                pickle.dump(group_table,file=f)

            # saving group table as json (for frontend only)
            group_table.set_index('DEVICE_NAME',inplace=True)
            group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
            with open(config['data_path']+'DeviceSpecific/Device_data/group_table.json','r') as f:
                group_table = json.load(f)
            with open (config['data_path']+'DeviceSpecific/Device_data/group_table.json','w') as f:
                json.dump(group_table,fp=f,indent=5)

    ########## FUNCTION TO RETURN GROUP TABLE AS PANDAS DF
    @logExceptionsWrapper
    def retrieveGroupTable(self):
        group_table = None
        if isfile(config['data_path']+'DeviceSpecific/Device_data/group_table'):
            with open(config['data_path']+'DeviceSpecific/Device_data/group_table','rb') as f:
                group_table = pickle.load(f)
        return group_table

    ########## FUNCTION TO UPDATE GROUP TABLE ON PING
    @logExceptionsWrapper
    def updateLastPing(self,device_name):
        result = False
        group_table = self.retrieveGroupTable()
        if group_table is not None:
            try:
                device = group_table.loc[device_name]
                group_table.at[device_name,'LAST_PING'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                result = True
            
            except KeyError:
                result = False
            
            finally:
                # storing group table
                with open(config['data_path']+'DeviceSpecific/Device_data/group_table','wb') as f:
                    pickle.dump(group_table,file=f)
                # saving group table as json (for frontend only)
                group_table.set_index('DEVICE_NAME',inplace=True)
                group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
                with open(config['data_path']+'DeviceSpecific/Device_data/group_table.json','r') as f:
                    group_table = json.load(f)
                with open (config['data_path']+'DeviceSpecific/Device_data/group_table.json','w') as f:
                    json.dump(group_table,fp=f,indent=5)
        return result

    ########## FUNCITON TO ADD DEVICE TO GROUP TABLE
    @logExceptionsWrapper
    def addDeviceToGroupTable(self,ip, port,device_name,pub_key,future_master=False):
        result = False
        if self.master:
            group_table = self.retrieveGroupTable()

            if group_table is not None:
                try:
                    device = group_table.loc[device_name]
                    device['LAST_PING'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    result = False
                except KeyError:
                    new_device = {
                        'DEVICE_NAME':device_name,
                        'IP':ip,
                        'PORT':port,
                        'PUB_KEY': pub_key,
                        'TIMESTAMP':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'LAST_PING':datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    if future_master:
                        new_device['MPRECIDENCE'] = group_table['MPRECIDENCE'].max() + 1
                    else :
                        new_device['MPRECIDENCE'] = -1
                    group_table = group_table.append(new_device,ignore_index=True)
                    result = True
                finally:
                    # storing group table
                    with open(config['data_path']+'DeviceSpecific/Device_data/group_table','wb') as f:
                        pickle.dump(group_table,file=f)
                    # saving group table as json (for frontend only)
                    group_table.set_index('DEVICE_NAME',inplace=True)
                    group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
                    with open(config['data_path']+'DeviceSpecific/Device_data/group_table.json','r') as f:
                        group_table = json.load(f)
                    with open (config['data_path']+'DeviceSpecific/Device_data/group_table.json','w') as f:
                        json.dump(group_table,fp=f,indent=5)

        return result

    ############################## FOLLOWING ARE FUNCTION ON THE BLOCKCHAIN ##############################

    ########## FUNCITON TO CREATE A NEW GROUP ONTO THE BLOCKCHIAN
    @logExceptionsWrapper
    def createNewGroup(self,host = '127.0.0.1'):
        if self.master :
            tx = {
                    'from':bcc.eth.default_account,
                    'value':bcc.toWei(1,'ether')
                }

            group_creation_possible = contract.functions.addGroup(
                self.master_key,
                self.device_name,
                self.public_key_serialized.decode(),
                ('%s:%s:%s:%s')%(public_ip,private_ip,host,self.device_name),
                10
            ).call(tx)

            if group_creation_possible:

                tx_hash = contract.functions.addGroup(
                    self.master_key,
                    self.device_name,
                    self.public_key_serialized.decode(),
                    ('%s:%s:%s:%s')%(public_ip,private_ip,host,self.port),
                    10
                ).transact(tx)
                tx_receipt = bcc.eth.wait_for_transaction_receipt(tx_hash)

                # storing group creation transaction receipt
                with open(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt','wb') as f:
                    pickle.dump(tx_receipt,f)

                # creating group table
                self.createGroupTable()
                return True
        return False

    ########## FUNCTION TO VERIFY GROUP CREATION TRNASACTION RECEIPT
    @logExceptionsWrapper
    def verifyGroupCreation(self,tx_receipt):
        try:
            log = contract.events.GroupCreation().processLog(tx_receipt.logs[1])
            return True
        except Exception as e:
            return False

    ########## FUNCTION TO CREATE A NEW DEVICE, ONTO THE BLOCKCHAIN
    @logExceptionsWrapper
    def createNewDevice(self,host = '127.0.0.1'):

        device_association_possible = contract.functions.addDevice(
            self.master_key,
            self.device_name,
            self.public_key_serialized.decode(),
            ('%s:%s:%s:%s')%(public_ip,private_ip,host,self.port),
            self.future_master
        ).call()

        if device_association_possible:
            
            tx_hash = contract.functions.addDevice(
                self.master_key,
                self.device_name,
                self.public_key_serialized.decode(),
                ('%s:%s:%s:%s')%(public_ip,private_ip,host,self.port),
                self.future_master
            ).transact()
            tx_receipt = bcc.eth.wait_for_transaction_receipt(tx_hash)
            
            # storing device association transaction receipt
            with open(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt','wb') as f:
                pickle.dump(tx_receipt,f)
            
            return True
        return False 

    ########## FUNCTION TO VERIFY DEVICE ASSOCIATION TRANSACTION RECEIPT
    @logExceptionsWrapper
    def verifyDeviceAssociation(self,tx_receipt):
        try:
            log = contract.events.DeviceAssociation().processLog(tx_receipt.logs[0])
            return True
        except Exception as e:
            return False

    ######### FUNCTION TO ADD DATA MESSAGE TO BLOCKCHAIN
    @logExceptionsWrapper
    def addMessage(self,messageFileName):

        if isfile(messageFileName):
            msg = None
            with open(messageFileName) as f:
                msg = json.load(f)

            #check if to_device exist and get corresponding public key from group table
            group_table_df = self.retrieveGroupTable()
            group_table_df.set_index('DEVICE_NAME',inplace=True)
            # print (group_table_df)
            try :
                to_device = group_table_df.loc[msg['to_device_name']]

                message_id = str(random())
                to_public_key = to_device['PUB_KEY']
                discard, to_public_key = loadKeyPairRSA(to_public_key,self.master_key)

                en_msg_data = encryptRSA(to_public_key,msg['data_message'])

                # converting encrypted to string without affecting encoding
                en_msg_data = list(en_msg_data)
                en_msg_data = [str(item) for item in en_msg_data]
                en_msg_data = '-'.join(en_msg_data)

                valid_transaction = contract.functions.addMessage(
                    self.master_key,
                    self.device_name,
                    msg['to_device_name'],
                    message_id,
                    en_msg_data
                ).call()


                if valid_transaction:
                    tx_hash = contract.functions.addMessage(
                        self.master_key,
                        self.device_name,
                        msg['to_device_name'],
                        message_id,
                        en_msg_data    
                    ).transact()
                    tx_receipt = bcc.eth.wait_for_transaction_receipt(tx_hash)
                    msg['tx_receipt']  = config['data_path']+'DeviceSpecific/Transaction_receipt/MessageTransactionReceipt.%s'%(message_id)
                    msg['port'] = str(to_device['PORT'])
                    msg['message_id'] = message_id
                    with open(messageFileName,'w') as f:
                        json.dump(msg,fp=f,indent=4)
                    with open(msg['tx_receipt'],'wb') as f:
                        pickle.dump(tx_receipt,f)
                    rename(messageFileName,messageFileName.replace('.pending','.pending.ping'))

            except KeyError:
                device_logger.warning('UNKNOW DEVICE : '+msg['to_device_name'])

    ########## FUNCTION TO MESSAGE TRANSACTION RECEIPT
    @logExceptionsWrapper
    def verifyMessageTransaction(self,tx_receipt):
        try:
            log = contract.events.MessageTransaction().processLog(tx_receipt.logs[0])
            return True
        except Exception as e:
            return False

    ######### FUNCTION TO READ DATA MESSAGE FROM BLOCKCHAIN
    @logExceptionsWrapper
    def getMessage(self,msg,port):
        from_device_name = contract.functions.retrieveMessageFromDevice(
            self.master_key,
            self.device_name,
            msg['message_id']
        ).call()
        print (from_device_name)

        # reject on duplicate identity
        group_table_df = self.retrieveGroupTable()
        group_table_df.set_index('DEVICE_NAME',inplace=True)
        suspect = False
        try : 
            from_device = group_table_df.loc[from_device_name]
            if port != from_device['PORT']:
                suspect = True
        except :
            suspect = True

        # get data and store in inbox
        cipher_text = contract.functions.retrieveMessageData(
            self.master_key,
            self.device_name,
            msg['message_id']
        ).call()

        cipher_text = cipher_text.split('-')
        cipher_text = [int(item) for item in cipher_text]
        cipher_text = bytes(cipher_text)
        data_message = decryptRSA(self.private_key,cipher_text)
        # write and return incoming message 
        write_msg = {
            'suspect' : suspect,
            'message_id' : msg['message_id'],
            'from_device_name' : from_device_name,
            'tx_receipt' : config['data_path']+'DeviceSpecific/Transaction_receipt/MessageTransactionReceipt.%s'%(msg['message_id']),
            'data_message' : data_message
        }
        with open(config['data_path']+'DeviceSpecific/Inbox/%s.json'%(msg['message_id']),'w') as f:
            # from_device = group_table_df.loc[from_device_name]
            json.dump(
                write_msg,
                fp=f,
                indent=5
            )
        with open(write_msg['tx_receipt'],'wb') as f:
            pickle.dump(msg['message_tx_eceipt'],f)

        return write_msg