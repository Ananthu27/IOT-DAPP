########## here blockchain default account is set based on subsciber
from web3 import Web3
import json
from blockChain import getAbiAndBytecode

config = None
with open('config.json') as f:
    config = json.load(f)

ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[1]
abi , disacrd = getAbiAndBytecode(config['contract_path']+'Storage.sol')
contract = bcc.eth.contract(address=config['address'],abi=abi)

########### FUNCTION TO VERIFY GROUP CREATION TRNASACTION RECEIPT
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