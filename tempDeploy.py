from web3 import Web3
import json
from blockChain import getAbiAndBytecode, deploy

config = None
with open('config.json') as f:
	config = json.load(f)

ganache_url = config['ganache_endpoint']

web3 = Web3(Web3.HTTPProvider(ganache_url))

def deploy_write_addr():
	web3.eth.default_account = web3.eth.accounts[0]
	receipt = deploy(config['contract_path']+'Storage.sol',web3)
	with open('config.json','w') as f:
		config['address'] = receipt.contractAddress
		json.dump(config,f)

deploy_write_addr()