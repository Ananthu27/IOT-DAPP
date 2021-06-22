########## here blockchain default account is set based on subsciber
from web3 import Web3
import json
import pickle
from blockChain import getAbiAndBytecode

config = None
with open('config.json') as f:
    config = json.load(f)

ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[int(config['default_subsciber_accout'])]
abi , disacrd = getAbiAndBytecode(config['main_contract_path'])
contract = bcc.eth.contract(address=config['address'],abi=abi)

from crypto import retrieveKeyPairRsa
from network import getPublicPirvateIp
from device_functions import createGroupTable

########## FUNCITON TO CREATE A NEW GROUP
def createNewGroup(master_key,host,public_key_serialized):
    tx = {
            'from':bcc.eth.default_account,
            'value':bcc.toWei(1,'ether')
        }
    private_ip, public_ip = getPublicPirvateIp()
    my_device = None
    with open(config['data_path']+'DeviceSpecific/Device_data/myDevice.json','r') as f:
        my_device = json.load(f)

    group_creation_possible = contract.functions.addGroup(
        master_key,
        my_device['device_name'],
        public_key_serialized.decode(),
        ('%s:%s:%s:%s')%(public_ip,private_ip,host,my_device['port']),
        10
    ).call(tx)

    if group_creation_possible:
        tx_hash = contract.functions.addGroup(
            master_key,
            my_device['device_name'],
            public_key_serialized.decode(),
            ('%s:%s:%s:%s')%(public_ip,private_ip,host,my_device['port']),
            10
        ).transact(tx)
        tx_receipt = bcc.eth.wait_for_transaction_receipt(tx_hash)
        # storing group creation transaction receipt
        with open(config['data_path']+'DeviceSpecific/Transaction_receipt/GroupCreationReceipt','wb') as f:
            pickle.dump(tx_receipt,f)
        # creating group table
        createGroupTable(my_device['port'],my_device['device_name'],master_key)
        return True
    return False
 

########## FUNCTION TO VERIFY GROUP CREATION TRNASACTION RECEIPT
def verifyGroupCreation(tx_receipt):
    try:
        log = contract.events.GroupCreation().processLog(tx_receipt.logs[0])
        return True
    except Exception as e:
        return False
        
########## FUNCTION TO VERIFY DEVICE ASSOCIATION TO GROUP TRANSACTION RECEIPT
def verifyDeviceAssociation(tx_receipt):
    try:
        return True
    except Exception as e:
        return False