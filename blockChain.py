from solc import compile_standard
import json
from web3._utils.empty import Empty

########## custom exceptions ... move to common exceptions.py file soon

from exceptions import NoneValuedPars, EmptyDefaultAccount, FileExtError

########## FUNCTION TO COMPILE SOLIDITY CODE AND RETURN THE ABI AND BYTECODE ... PROVIDE ABSOLUTE PATH AS PARAMETER
def getAbiAndBytecode(file_path=None):
    if file_path is not None:
        if file_path.endswith('.sol'):

            sol_code = None
            filename = file_path.split('/')[-1]
            
            with open(file_path) as f:
                sol_code = f.read()
            
            compiled_sol = compile_standard({
                "language": "Solidity",
                "sources": {
                    filename : {
                        "content": sol_code
                    }
                },
                "settings" : {
                    "outputSelection": {
                        "*": {
                            "*": [
                                "metadata", "evm.bytecode"
                                , "evm.bytecode.sourceMap"
                            ]
                        }
                    }
                }
            })
            
            # bytecode = compiled_sol['contracts'][filename][Classname(assumend as filename without ".sol")]['evm']['bytecode']['object']
            bytecode = compiled_sol['contracts'][filename][filename.split('.')[0]]['evm']['bytecode']['object']
            
            # abi = json.loads(compiled_sol['contracts']['Greeter.sol'][Classname(assumend as filename without ".sol")]['metadata'])['output']['abi']
            abi = json.loads(compiled_sol['contracts'][filename][filename.split('.')[0]]['metadata'])['output']['abi']

            return abi, bytecode

        else :
            raise FileExtError(required='.sol(Solidity file)',function=__file__+'.getAbiAndBytecode()')
    else :
        raise NoneValuedPars(varname='file_path',function=__file__+'.getAbiAndBytecode()')

########## FUNCTION TO DEPLOY CONTRACT TO BLOCKCHAIN
def deploy(file_path=None,bc_conn=None):
    ########## assumption : default account is set on the bc_conn
    if bc_conn is not None: 
        if type(bc_conn.eth.default_account) != Empty :
            
            abi, bytecode = getAbiAndBytecode(file_path)
            
            Contract = bc_conn.eth.contract(abi=abi,bytecode=bytecode)
            tx_hash = Contract.constructor().transact()
            tx_receipt = bc_conn.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_receipt
        else :
            raise EmptyDefaultAccount(function=__file__+'.deploy()')
    else :
        raise NoneValuedPars(varname='bc_conn',function=__file__+'.deploy()')


# from web3 import Web3

# config = None

# with open('config.json') as f:
#     config = json.load(f)

# ganache_url = config['ganache_endpoint']

# web3 = Web3(Web3.HTTPProvider(ganache_url))
# web3.eth.default_account = web3.eth.accounts[0]

# receipt = deploy('/ANNA/PROJECT/IOT-DAPP/Contracts/Storage.sol',web3)