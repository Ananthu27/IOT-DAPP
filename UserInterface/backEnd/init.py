########## ALL IMPORTS FROM FLASK
from flask import Flask
from flask_cors import CORS, cross_origin

########## ALL GENERAL IMPORTS 
import json 
import pickle
from os.path import isfile
from os import listdir

######### CREATING FLASK APP
server = Flask('BC_Backend')
CORS(server,supports_credentials=True)

######### SETTING CONFIG HERE
server.config['TransactionsPath'] = '../../Data/DeviceSpecific/Transaction_receipt/'
server.config['DeviceDataPath'] = '../../Data/DeviceSpecific/Device_data/'
server.config['OutboxPath'] = '../../Data/DeviceSpecific/Outbox/'
server.config['InboxPath'] = '../../Data/DeviceSpecific/Inbox/'
server.config['LogsPath'] = '../../Logs/'
server.config['ContractPath'] = '../../Contracts/Storage.sol'
from web3 import Web3
from blockChain import getAbiAndBytecode

config = None
with open('../../config.json') as f:
    config = json.load(f)

ganache_url = config['ganache_endpoint']
bcc = Web3(Web3.HTTPProvider(ganache_url))
bcc.eth.default_account = bcc.eth.accounts[int(config['default_subsciber_accout'])]
abi , disacrd = getAbiAndBytecode(server.config['ContractPath'])
contract = bcc.eth.contract(address=config['address'],abi=abi)

def delTypeInDict(data_dict,data_type):
    temp = {}
    for key in data_dict.keys():
        if type(data_dict[key]) != data_type:
            temp[key] = data_dict[key]
    return temp

def delTypeInList(data_list,data_type):
    temp = []
    for item in data_list:
        if type(item) != data_type:
            temp.append(item)
    return temp

########## SERVER ROUTES FROM HERE ON

########## HOME ROUTE
@server.route('/')
@server.route('/flask/home')
@server.route('/flask/info')
def info():
    return 'BlockChain backend server running.'

########## ALL PATHS HERE ON RETURN JSON DATA

# http://127.0.0.1:5000/flask/GroupTable
########## PATH TO RETURN GROUP TABLE
# @server.route('/flask/GroupTable',methods=['GET'])
# @cross_origin(supports_credentials=True)
# def getGroupTable():
#     response = json.dumps({})
#     if isfile(server.config['DeviceDataPath']+'group_table.json'):
#         with open(server.config['DeviceDataPath']+'group_table.json','r') as f:
#             response = json.load(f)
#     # response =[response]
#     response = json.dumps(response)
#     return response

@server.route('/flask/GroupTable',methods=['GET'])
@cross_origin(supports_credentials=True)
def getGroupTable():
    response = json.dumps([])

    if isfile(server.config['DeviceDataPath']+'group_table'):
        with open(server.config['DeviceDataPath']+'group_table','rb') as f:
            df = pickle.load(f)

            indexs = df.index
            columns = df.columns
            response = []

            for index in indexs:
                item = {}
                for column in columns:
                    item[column] = str(df.loc[index][column])
                response.append(item)

    return json.dumps(response)
# http://127.0.0.1:5000/flask/TransactionNames
########## PATH TO RETURN LIST OF ALL TRANSACTION RECEIPT NAMES
@server.route('/flask/TransactionNames',methods=['GET'])
@cross_origin(supports_credentials=True)
def getTranscationsList():
    response = listdir(server.config['TransactionsPath'])
    return json.dumps(response)

# http://127.0.0.1:5000/flask/Transaction/GroupCreationReceipt
# http://127.0.0.1:5000/flask/Transaction/MessageTransactionReceipt.0.6270150798418231
########## PATH TO RETURN TRANSACTION RECEIPT
@server.route('/flask/Transaction/<string:filename>',methods=['GET'])
@cross_origin(supports_credentials=True)
def getTransaciton(filename):
    response = json.dumps({})
    if isfile(server.config['TransactionsPath']+filename):
        with open(server.config['TransactionsPath']+filename,'rb') as f:
            tx_receipt = pickle.load(f)
            response = tx_receipt.__dict__
            response['logs'] = [item.__dict__ for item in response['logs']]
            del_type = type(response['transactionHash'])
            response = delTypeInDict(response,del_type)
            response['logs'] = [delTypeInDict(item,del_type) for item in response['logs']]
            for i,log in enumerate(response['logs']):
                response['logs'][i]['topics'] = delTypeInList(response['logs'][i]['topics'],del_type)
            response=[response]
            response = json.dumps(response,indent=4)
    return (response)

# http://127.0.0.1:5000/flask/Logs/5
########## PATH TO RETURN LAST N LOGS
@server.route('/flask/Logs/<int:n_lines>',methods=['GET'])
@cross_origin(supports_credentials=True)
def getLogs(n_lines):
    response = []
    if isfile(server.config['LogsPath']+'ServerLog.log'):
        with open(server.config['LogsPath']+'ServerLog.log') as f:
            lines = f.readlines()
            action = 0
            item = {}
            item['content'] = []
            for i,line in enumerate(lines):

                if line == '\n' :
                    action = 0
                    response.append(item)
                    item = {}
                    item['content'] = []

                elif i == len(lines)-1 and action==1:
                    item['content'].append(line)
                    response.append(item)

                elif action == 0 :
                    action = 1
                    content = line.split('::')
                    item['dateTime'] = content[0]
                    item['level'] = content[1]

                elif action == 1 :
                    if '\n' in line:
                        line = line.replace('\n','')
                    item['content'].append(line)
        item = {}
        item['content'] = []

        while item in response:
            response.remove(item)

        response = response[-n_lines:]

    return json.dumps(response)
    
# http://127.0.0.1:5000/flask/Device/Master1
########## PATH TO RETURN DEVICE DETAILS
@server.route('/flask/Device/<string:device_name>',methods=['GET'])
@cross_origin(supports_credentials=True)
def getDevice(device_name):
    response = json.dumps({})
    try : 
        device = contract.functions.devices(device_name).call()
        response = {
            'exists' : device[0],
            'device_name' : device[1],
            'public_key' : device[2],
            'public_ip':device[3],
            # 'private_ip':device[4],
            # 'host':device[5],
            # 'port' : device[6],
            'master' : device[4],
            'future_master' : device[5],
        }
        response =[response]
        response = json.dumps(response)
    except Exception as e: 
        print (e)
    return response

if __name__ == '__main__':
    server.run(debug=True)