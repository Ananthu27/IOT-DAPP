######### here blockchain default account is set based on subsciber

######### GENEARAL IMPORTS
from web3 import Web3
import json
import pickle
from urllib.request import urlopen
from os.path import isfile

########## USER DEFINED FUNCTION IMPORTS
from exceptions import PayloadExceedsUdpMtu
from blockChain import getAbiAndBytecode, logExceptionsWrapper

########## IMPORTS FOR LOGGING
from logger import createLogger
from logging import INFO, log
from functools import wraps

message_logger = createLogger(name='Device',level=INFO,state='DEVELOPMENT')

from web3 import Web3
from blockChain import getAbiAndBytecode

config = None
with open('config.json') as f:
    config = json.load(f)

########## CONNECTING TO BLOCKCHAIN HERE
ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[int(config['default_subsciber_accout'])]
abi , disacrd = getAbiAndBytecode(config['main_contract_path'])
contract = bcc.eth.contract(address=config['address'],abi=abi)

########## FUNCTION TO GET TRUE RANDOM NUMBER
def getTrueRandom(length=10):
    url = 'https://www.random.org/sequences/?min=0&max=9&col=%d&format=plain&rnd=new'%(int(length))
    nonce = None
    response = urlopen(url).read()
    response = response.decode()
    nonce = response.replace('\t','').replace('\n','')
    return nonce

########## FUNCTION TO HANDLE ALL TYPES OF MESSAGES
class Message:

    ########## WRAPPER FOR LOGGER
    def logExceptionsWrapper(function):
        @wraps(function)
        def logExceptions(*args,**kwargs):
            try:
                return function(*args,**kwargs)
            except:
                print ('################# MESSAGE(CLASS) ERROR ###############')
                message_logger.exception('exception in device_functions.py.%s'%(function.__name__))
                print ('exception in device_functions.py.%s'%(function.__name__))
                print ('################# MESSAGE(CLASS) ERROR ###############')
        return logExceptions
        
    ########## FUNCTION TO UN PICKLE MESSAGE
    @logExceptionsWrapper
    def getMessage(self,msg):
        try :
            return pickle.loads(msg)
        except:
            return None

    ########## FUNCTION TO CREATE MESSAGE TO EXCHANGE PUBLIC KEY
    @logExceptionsWrapper
    def getPublicKeyMessage(self,device_object,to_port=None,nonce=None):
        
        # if nonce exist its a reply message and nonce need not be saved/recorded
        if to_port is not None and nonce is None:
            nonce = getTrueRandom()
            device_object.last_nonce[str(to_port)] = nonce
        msg = {
            'message_no' : '0',
            'nonce' : nonce,
            'public_key_serialized' : device_object.public_key_serialized
        }
        msg = pickle.dumps(msg)
        if len(msg) >= (2**16-8):
            raise(PayloadExceedsUdpMtu(size=len(msg),function=__file__+'.getPublicKeyMessage()'))
        return msg

    ######### FUNCTION TO CREATE ASSOCIATION REQUEST MESSAGE
    @logExceptionsWrapper
    def getAssociationRequestMssg(self,device_object,to_port):

        tx_receipt = None
        # check if association transaction is present
        if isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt'):
            with open (config['data_path']+'DeviceSpecific/Transaction_receipt/DeviceAssociationReceipt','rb') as f:
                tx_receipt = pickle.load(f)
        
        nonce = getTrueRandom()
        device_object.last_nonce[str(to_port)] = nonce

        msg = {
            'message_no' : '1',
            'nonce' : nonce,
            'device_name' : device_object.device_name,
            'public_key_serialized' : device_object.public_key_serialized,
            'future_master' : device_object.future_master,
            'association_tx_receipt' : tx_receipt
        }
        msg = pickle.dumps(msg)
        
        if len(msg) >= (2**16-8):
            raise(PayloadExceedsUdpMtu(size=len(msg),function=__file__+'.getPublicKeyMessage()'))
        
        return msg
    
    ######### FUNCTION TO CREATE ASSOCIATION REQUEST MESSAGE
    @logExceptionsWrapper
    def getAssociationResponseMssg(self,device_object,nonce):
        msg = None
        if device_object.master:
            if isfile(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt') :
                with open (config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt','rb') as f:
                    tx_receipt = pickle.load(f)
                    group_table_df = device_object.retrieveGroupTable()
                    msg = {
                        'message_no' : '2',
                        'nonce' : nonce,
                        'group_creation_tx_receipt' : tx_receipt,
                        'group_table' : group_table_df
                    }
                msg = pickle.dumps(msg)
                if len(msg) >= (2**16-8):
                    raise(PayloadExceedsUdpMtu(size=len(msg),function=__file__+'.getPublicKeyMessage()'))
        return msg