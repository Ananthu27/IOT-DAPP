########## here blockchain default account is set based on subsciber
from network import getPorts
import socket 
import traceback
from crypto import retrieveKeyPairRsa

host = '127.0.0.1'
master = True
new_group = True
master_key = 'Em0C2Kv9pM'
device_name = 'testMaster'

port_list = getPorts()
if '1111' not in port_list and master:
    port = 1111
    
else :
    port = None
    for i in range (6*10**4,6*10**4+2**12,2):
        if str(i) not in port_list:
            port = i
            break

########## this is the main frame 
import json
from web3 import Web3
from blockChain import getAbiAndBytecode
from network import getPublicPirvateIp
from device_functions import createGroupTable, retrieveGroupTable, storeMyDevice
from device_functions import getPublicKeyMessage, getMessage
from contract_functions import createNewGroup

########## LOADING CONFIGURATION HERE
config = None
with open('config.json') as f:
    config = json.load(f)

########## WRITING NEW DEVICE DATA HERE
storeMyDevice(port,device_name)

ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[1]
abi, discard = getAbiAndBytecode(config['main_contract_path'])
contract = bcc.eth.contract(address=config['address'],abi=abi)

private_key_serialized, public_key_serialized = retrieveKeyPairRsa(master_key,serialize=True)

# if this device is a master device
if master:
    if new_group:

        new_group_created = createNewGroup(master_key,public_key_serialized)
        
        if new_group_created:
            # continue infinite while loop
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                try:
                    s.bind((host, port))
                    while True:
                        # getting incoming message and message number
                        msg, address = s.recvfrom(1024)
                        msg = getMessage(msg)
                        message_no = msg['message_no']

                        ########### ANSWER DIFFERNET MESSAGES HERE

                        ########### PUBLIC KEY EXCHANGE MESSAGES HANDLED HERE, MESSAGE NUMBER = 0
                        if message_no == 0:
                            nonce = msg['nonce']
                            response_msg = getPublicKeyMessage(master_key,nonce)
                            s.sendto(msg,address)
                except OSError:
                    print ('Port :',port,'taken')
                except :
                    traceback.print_exc()
                finally:
                    s.close()
        # if new group cannot be created
        else :
            print ('group or device already exists')
# if device is not master
else:
    print ('not master')
