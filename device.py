from blockChain import logExceptionsWrapper
import pandas as pd
from network import getPublicPirvateIp
from datetime import datetime
from crypto import retrieveKeyPairRsa
import json 
from os import listdir
from os.path import isfile
import pickle
from crypto import retrieveKeyPairRsa

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

    ########## FUNCTION TO CREATE GROUP TABLE
    @logExceptionsWrapper
    def createGroupTable(self):
        if self.master :
            group_table = pd.DataFrame()
            # columns=['IP','PORT','DEVICE_NAME','PUB_KEY','TIMESTAMP','MPRECIDENCE','LAST_PING']
            private_ip, public_ip = getPublicPirvateIp()
            discard, public_key_serialized = retrieveKeyPairRsa(self.master_key,True)

            group_table['IP'] = [('%s::%s')%(private_ip,public_ip)]
            group_table['PORT'] = [self.port]
            group_table['DEVICE_NAME'] = [self.device_name]
            group_table['PUB_KEY'] = [public_key_serialized]
            group_table['TIMESTAMP'] = [datetime.now()]
            group_table['MPRECIDENCE'] = [0]
            group_table['LAST_PING'] = [datetime.now()]
            group_table = group_table.set_index('DEVICE_NAME')

            group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')

    ########## FUNCTION TO RETURN GROUP TABLE AS PANDAS DF
    @logExceptionsWrapper
    def retrieveGroupTable(self):
        group_table = None
        if 'group_table.json' in listdir(config['data_path']+'DeviceSpecific/Device_data/'):
            group_table = pd.read_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
        return group_table

    ########## FUNCTION TO UPDATE GROUP TABLE ON PING
    @logExceptionsWrapper
    def updateLastPing(self,device_name):
        result = False
        if self.master:
            group_table = self.retrieveGroupTable()
            if group_table is not None:
                try:
                    device = group_table.loc[device_name]
                    device['LAST_PING'] = datetime.now()
                    result = True
                except KeyError:
                    result = False
                finally:
                    group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
        return result

    ########## FUNCITON TO ADD DEVICE TO GROUP TABLE
    @logExceptionsWrapper
    def addDeviceToGroupTable(self,ip, port,device_name,pub_key,master=False):
        result = False
        if self.master:
            group_table = self.retrieveGroupTable()

            if group_table is not None:
                try:
                    device = group_table.loc[device_name]
                    device['LAST_PING'] = datetime.now()
                    result = False
                except KeyError:
                    group_table.loc[device_name]['IP'] = ip
                    group_table.loc[device_name]['PORT'] = port
                    # group_table.loc[device_name]['DEVICE_NAME'] = device_name
                    group_table.loc[device_name]['PUB_KEY'] = pub_key
                    group_table.loc[device_name]['TIMESTAMP'] = datetime.now()
                    if master:
                        group_table.loc[device_name]['MPRECIDENCE'] = group_table['MPRECIDENCE'].max() + 1
                    else :
                        group_table.loc[device_name]['MPRECIDENCE'] = -1
                    group_table.loc[device_name]['LAST_PING'] = datetime.now()
                    result = True
                finally:
                    group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')

        return result

    ########## FUNCITON TO CREATE A NEW GROUP
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

    ########## FUNCTION TO CREATE A NEW DEVICE
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

    ########## FUNCTION TO VERIFY GROUP CREATION TRNASACTION RECEIPT
    @logExceptionsWrapper
    def verifyGroupCreation(self,tx_receipt):
        try:
            log = contract.events.GroupCreation().processLog(tx_receipt.logs[0])
            return True
        except Exception as e:
            return False

    ########## FUNCTION TO VERIFY DEVICE ASSOCIATION TO GROUP TRANSACTION RECEIPT
    @logExceptionsWrapper
    def verifyDeviceAssociation(self,tx_receipt):
        try:
            log = contract.events.DeviceAssociation().processLog(tx_receipt.logs[0])
            return True
        except Exception as e:
            return False