from web3 import Web3
import json
from blockChain import getAbiAndBytecode, deploy

config = None
with open('config.json') as f:
	config = json.load(f)

ganache_url = config['ganache_endpoint']

web3 = Web3(Web3.HTTPProvider(ganache_url))

def deploy_write_addr():
	web3.eth.default_account = web3.eth.accounts[int(config['default_deployer_account'])]
	receipt = deploy(config['main_contract_path'],web3)
	with open('config.json','w') as f:
		config['address'] = receipt.contractAddress
		json.dump(config,fp=f,indent=4)

deploy_write_addr()