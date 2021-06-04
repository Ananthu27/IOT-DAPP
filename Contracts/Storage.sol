// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract Storage {

    bool internal busy = false;
    address payable deploy_wallet;

    // STRUCTURE TO STORE DEVICE INFORMATION
    struct device_info {
        bool exist;
        string device_name;
        string public_key;
        string public_address;
        bool master;
        bool future_master;
    }

    // STRUCTURE TO STORE GROUP INFORMATION
    struct group_info {
        bool exist;
        address owner;
        device_info master_device;
        uint256 max_size;
        uint256 tokens;
        string[] followers;
    }

    string public txt;

    // MAPPING CONTAINTING ALL GROUP DETAILS, CAN ONLY BE ACCESSED BY GROUP MEMBERS 
    mapping(string => group_info) private groups;

    // MAPPING CONTAINING ALL DEVICE DETAILS, CAN BE ACCESSED BY AYONE WHO KNOWS DEVICE NAME
    mapping(string => device_info) public devices;

    // FUNCTION TO CHECK IF GROUP ALREADY EXIXTS
    function groupExists(string memory secret_key) public view returns (bool){
        return (groups[secret_key].exist);
    }

    // FUNCTION TO CHECK IF DEVICE IS A FOLLOWER OF GROUP
    function followerExists(
        string memory secret_key,
        string memory _device_name
    )public returns (uint256){
        if(
            groupExists(secret_key) &&
            devices[_device_name].exist
        ){
            for(uint i=0; i<groups[secret_key].followers.length; i++){
                if(keccak256(bytes(groups[secret_key].followers[i])) == keccak256(bytes(_device_name)))
                    return i+1;
            }
            return 0;
        }
    }

    constructor(address payable _deploy_wallet) {
        deploy_wallet = _deploy_wallet;
    }

    // FUNCTION TO ADD A NEW GROUP, TOKEN COST 5
    function addGroup(
        string memory secret_key,
        string memory master_name,
        string memory master_public_key,
        string memory master_public_address,
        uint256 follower_count
    ) public payable returns(bool) {

        if(!groupExists(secret_key) && msg.value>=10**18){

            //transfer funds 
            deploy_wallet.transfer(msg.value);

            device_info memory master;
            master.exist = true;
            master.device_name = master_name;
            master.public_key = master_public_key;
            master.public_address = master_public_address;
            master.master = true;
            master.future_master = true;

            // adding master as new device
            devices[master_name] = master;

            // creating/adding the new group
            groups[secret_key] = group_info({
                exist: true,
                owner: msg.sender,
                master_device: master,
                max_size: follower_count,
                tokens: (msg.value/10**18)*1000-5,
                followers: new string[](0)
            });

            groups[secret_key].followers.push(master_name)

            return true;
        }
        return false;
    }
    
    // FUNCTION TO RECHARGE TOKENS
    function rechargeTokens(string memory secret_key) public payable returns (bool){

        if (groupExists(secret_key) && msg.value >= 10**18){
            deploy_wallet.transfer(msg.value);
            groups[secret_key].tokens += (msg.value/10**18)*1000;
            return true;
        }
        return false;
    }

    // FUNCTION TO ADD A NEW DEVICE, token cost 1
    function addDevice(
        string memory secret_key,
        string memory _device_name,
        string memory _public_key,
        string memory _public_address,
        bool memory _future_master
    ) public returns (bool){

        // if group exist and device doesnt exist then
        if(
            groupExists(secret_key) 
            && !devices[_device_name].exist 
            && groups[secret_key].followers.length < groups[secret_key].max_size
        ){
            devices[_device_name] = device_info({
                exist: true,
                device_name: _device_name,
                public_key: _public_key,
                public_address: _public_address,
                master: false,
                future_master: _future_master
            });
            groups[secret_key].followers.push(_device_name);
            groups[secret_key].tokens -= 1;
            return (true);
        }

        // if group and device exists ... check if device already in group 
        else if(
            devices[_device_name].exist
            && groupExists(secret_key)
        ){

            if(followerExists(secret_key,_device_name))
                return true;

            // if device not in group add it. Enables single device multiple group
            groups[secret_key].followers.push(_device_name);
            return true;
        }

        return false;
    }

    // FUNCTION TO REMOVE A DEVICE FROM GROUP, token cost 1
    function removeDevice(
        string memory secret_key,
        string memory _device_name,
    )public returns (bool){
        
        index = followerExists(secret_key,_device_name);
        // check if device is part of group
        if(index){
            index -= 1;
            // check if index is correct
            if(index>=0 && index<groups[secret_key].followers.length){
                for (uint i=index; i<(groups[secret_key].followers.length-1) ; i++){
                    groups[secret_key].followers[i] = groups[secret_key].followers[i+1];
                }
                delete groups[secret_key].followers[groups[secret_key].followers.length-1];
                groups[secret_key].followers.length--;
                groups[secret_key].tokens -= 1;
                return true;
            }
        }
        return false;
    }

    // FUNCTION TO CHANGE MASTER, token cost 1
    function relinquishMaster(
        string memory secret_key,
        string memory _device_name
    ) public retunrs (bool){

        if (
            groupExists(secret_key) &&
            devices[_device_name].exist &&
            // cannot be master of two groups !
            !devices[_device_name].master &&
            devices[_device_name].future_master
        ){

            if(followerExists(secret_key,_device_name)){
                groups[secret_key].master = devices[_device_name];
                groups[secret_key].tokens -= 1;
                // remove master from followers as .... master is only replaced if and only if master dies.
                removeDevice(secret_key,_device_name);
                return true;
            }

        }
        return false;
    }
}