# device IP, Port, Unique Name, public key, timestamp of Joining, auto inc count(precidence for new master), last ping time

import pandas as pd
from network import getPublicPirvateIp
from datetime import datetime
from crypto import retrieveKeyPairRsa
from json import load
from os import listdir

config = None
with open('config.json','r') as f:
    config = load(f)

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
def retrieveGroupTable():
    group_table = None
    if 'group_table.json' in listdir(config['data_path']+'DeviceSpecific/Device_data/'):
        group_table = pd.read_json(config['data_path']+'DeviceSpecific/Device_data/group_table.json')
    return group_table

########## FUNCITON TO ADD DEVICE TO GROUP TABLE
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

addDeviceToGroupTable('test')