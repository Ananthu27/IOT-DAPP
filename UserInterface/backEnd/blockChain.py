from solc import compile_standard
import json

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
    return None,None