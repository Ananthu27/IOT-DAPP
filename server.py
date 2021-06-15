# https://www.random.org/sequences/?min=10&max=20&col=10&format=plain&rnd=new
from network import getPorts
import socket 
import traceback
from crypto import getKeyPairRSA,loadKeyPairRSA
import time
import random
import pickle

port_list = getPorts()
host = '127.0.0.1'

message = {
    '1' : 'PUBLIC KEY REQUEST'
}

# master_key = input('Enter the Master key : ')
# device_name = input('Enter device name : ')
new_group = True
master_key = 'Em0C2Kv9pM'
device_name = 'testMaster'


def deployServer(HOST,PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # master_key = 'testing'
        # private_key_serialized, public_key_serialized = getKeyPairRSA(serialize=True,master_key=master_key)
        try :
            print ('Establishing server at addr :',HOST,':',PORT)
            s.bind((HOST, PORT))
            # if master
            if PORT==1111:
                while True:
                    message , address = s.recvfrom(1024)
                    print ('recevied :',message,address)
                    ########### ANSWER DIFFERNET MESSAGES HERE
                    if message.decode() == '1':
                        s.sendto(public_key_serialized,address)
            # when follower
            else:
                while True:
                    s.sendto('1'.encode(),('127.0.0.1',1111))
                    message , addr = s.recvfrom(1024)
                    discard, master_public_key = loadKeyPairRSA(message,master_key)
                    print ('public key:',master_public_key)
                    time.sleep(10)
                        
        except OSError:
            print ('Port :',PORT,'taken')
        except :
            traceback.print_exc()
        finally:
            s.close()

server = None

if '1111' not in port_list and new_group:
    port = 1111
    
else :
    port = None
    for i in range (6*10**4,6*10**4+2**12,2):
        if str(i) not in port_list:
            port = i
            break

# deployServer(host,port)

########## this is the main frame 
import json
from web3 import Web3
from blockChain import getAbiAndBytecode
from network import getPublicPirvateIp

config = None

with open('/ANNA/PROJECT/IOT-DAPP/IgnoreFiles/config.json') as f:
    config = json.load(f)

ganache_url = config['ganache_endpoint']

bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[0]

if new_group:
    contract = None
    with open('/ANNA/PROJECT/IOT-DAPP/Data/General/config.json') as f:
        config = json.load(f)
        abi, discard = getAbiAndBytecode('/ANNA/PROJECT/IOT-DAPP/Contracts/Storage.sol')
        contract = bcc.eth.contract(address=config['address'],abi=abi)
    tx = {
        'from':bcc.eth.default_account,
        'value':bcc.toWei(1,'ether')
    }

    private_key_serialized, public_key_serialized = getKeyPairRSA(serialize=True,master_key=master_key)
    private_ip, public_ip = getPublicPirvateIp()
    gc = contract.functions.addGroup(
        master_key,
        device_name,
        public_key_serialized.decode(),
        ('%s:%s:%s:%s')%(public_ip,private_ip,host,port),
        10
    ).call(tx)
    if gc:
        tx_hash = contract.functions.addGroup(
            master_key,
            device_name,
            public_key_serialized.decode(),
            ('%s:%s:%s:%s')%(public_ip,private_ip,host,port),
            10
        ).transact(tx)
        # tx_receipt = bcc.eth.getTransactionReceipt(tx_hash)
        tx_receipt = bcc.eth.wait_for_transaction_receipt(tx_hash)
        with open('/ANNA/PROJECT/IOT-DAPP/Data/DeviceSpecific/Transaction_receipt/temp','wb') as f:
            pickle.dump(tx_receipt,f)
        print(tx_receipt)
        # decode logs here
        contract
    else :
        # from web3.eth.abi import decodeLog
        from web3.logs import IGNORE
        print ('masterkey or device name not valid')
        with open('/ANNA/PROJECT/IOT-DAPP/Data/DeviceSpecific/Transaction_receipt/temp','rb') as f:
            tx_receipt = pickle.load(f)
            # print (tx_receipt.logs[0].logIndex)
            # print ()
            # print (tx_receipt.logs[0].data) #para2
            # print ()
            # print (tx_receipt.logs[0].topics) #para3
            # result = decodeLog(
            #     [{'type':'group_info','name':'group'}],
            #     tx_receipt.logs[0].data,
            #     tx_receipt.logs[0].topics
            # )
            logs = contract.events.GroupCreation().processLog(tx_receipt.logs[0])
            print (logs)
