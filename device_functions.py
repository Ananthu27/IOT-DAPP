import pandas as pd
from network import getPublicPirvateIp
from datetime import datetime
from crypto import retrieveKeyPairRsa
from json import dump, load, dumps
from os import listdir
from os.path import isfile

config = None
with open('config.json','r') as f:
    config = load(f)

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO, log
from functools import wraps

device_logger = createLogger(name='Device',level=INFO,state='DEVELOPMENT')

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

########## FUNCTION TO CREATE GROUP TABLE
@logExceptionsWrapper
def createGroupTable(
    port,
    device_name,
    master_key
):
    group_table = pd.DataFrame()
    # columns=['IP','PORT','DEVICE_NAME','PUB_KEY','TIMESTAMP','MPRECIDENCE','LAST_PING']
    private_ip, public_ip = getPublicPirvateIp()
    discard, public_key_serialized = retrieveKeyPairRsa(master_key,True)

    group_table['IP'] = [('%s::%s')%(private_ip,public_ip)]
    group_table['PORT'] = [port]
    group_table['DEVICE_NAME'] = [device_name]
    group_table['PUB_KEY'] = [public_key_serialized]
    group_table['TIMESTAMP'] = [datetime.now()]
    group_table['MPRECIDENCE'] = [0]
    group_table['LAST_PING'] = [datetime.now()]
    group_table = group_table.set_index('DEVICE_NAME')

    group_table.to_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')

########## FUNCTION TO RETURN GROUP TABLE AS PANDAS DF
@logExceptionsWrapper
def retrieveGroupTable():
    group_table = None
    if 'group_table.json' in listdir(config['data_path']+'DeviceSpecific/Device_data/'):
        group_table = pd.read_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
    return group_table

########## FUNCTION TO UPDATE GROUP TABLE ON PING
@logExceptionsWrapper
def updateLastPing(device_name):
    group_table = retrieveGroupTable()
    result = False
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
def addDeviceToGroupTable(
    ip, port,
    device_name,
    pub_key,
    master=False,
    ):
    group_table = retrieveGroupTable()
    result = False

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

########## FUNCTION TO STORE MY DEVICE DETAILS AS JSON
@logExceptionsWrapper
def storeMyDevice(port,device_name):
    details = {
        'device_name' : device_name,
        'port' : port
    }
    with open(config['data_path']+'DeviceSpecific/Device_data/myDevice.json','w') as f:
        dump(details,f)


########################################                                           ##############################
######################################## MESSAGES AND MESSAGE REPLIES FROM HERE ON ##############################
########################################                                           ##############################

import pickle
from urllib.request import urlopen
from crypto import retrieveKeyPairRsa
from exceptions import PayloadExceedsUdpMtu

########## FUNCTION TO GET TRUE RANDOM NUMBER
@logExceptionsWrapper
def getTrueRandom(length=10):
    url = 'https://www.random.org/sequences/?min=0&max=9&col=%d&format=plain&rnd=new'%(int(length))
    nonce = None
    response = urlopen(url).read()
    response = response.decode()
    nonce = response.replace('\t','').replace('\n','')
    return nonce

########## FUNCTION TO UN PICKLE MESSAGE
@logExceptionsWrapper
def getMessage(msg):
    return pickle.loads(msg)

########## FUNCTION TO RECORD LAST NONCE
@logExceptionsWrapper
def storeNonce(port,nonce):
    last_nonce = None
    if isfile(config['data_path']+'DeviceSpecific/Device_data/last_nonce.json'):
        with open(config['data_path']+'DeviceSpecific/Device_data/last_nonce.json','r+') as f:
            last_nonce = load(f)
            last_nonce[port] = nonce
            dump(last_nonce,f) 
    else :
        with open(config['data_path']+'DeviceSpecific/Device_data/last_nonce.json','w') as f:
            last_nonce = {
                port : nonce
            }
            dump(last_nonce,f)

########## FUNCTION TO CREATE MESSAGE TO EXCHANGE PUBLIC KEY
@logExceptionsWrapper
def getPublicKeyMessage(master_key,to_port=None,nonce=None):
    discard, public_key_serialised = retrieveKeyPairRsa(master_key,serialize=True)

    # if nonce exist its a reply message and nonce need not be saved/recorded
    if to_port is not None and nonce is None:
        nonce = getTrueRandom()
        storeNonce(to_port,nonce)

    msg = {
        'message_no' : '0',
        'nonce' : nonce,
        'public_key_serialised' : public_key_serialised
    }
    msg = pickle.dumps(msg)
    if len(msg) >= (2**16-8):
        raise(PayloadExceedsUdpMtu(size=len(msg),function=__file__+'.getPublicKeyMessage()'))
    return msg

########## FUNCTION TO CREATE ASSOCIATION REQUEST MESSAGE
# @logExceptionsWrapper
# def getAssociationRequestMssg():
#     msg = None
#     # check if association transaction is present
#     if 'GroupCreationReceipt' in listdir(config['data_path']+'DeviceSpecific/Transaction_receipt/'):
#         with open (config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt','rb') as f:
#             tx_receipt = pickle.load(f)
#             msg = {
#                 'message_no' : '1',
#                 'nonce' : getTrueRandom(10),
#                 'association_tx_receipt' : tx_receipt
#             }
#             msg = pickle.dumps(msg)
#     return msg