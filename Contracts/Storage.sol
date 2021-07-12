// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract Storage {

    bytes32 test;
    address payable deploy_wallet;

    // STRUCTURE TO STORE DEVICE INFORMATION
    struct device_info {
        bool exist;
        string device_name;
        string public_key;
        string[] previous_keys;
        string public_address;
        bool master;
        bool future_master;
    }

    // STRUCTURE TO STORE GROUP INFORMATION
    struct group_info {
        bool exist;
        address owner;
        device_info master_device;
        string[] masters;
        uint8 max_size;
        uint256 tokens;
        string[] followers;
    }

    struct message_info {
        bool exist;
        string from_device_name;
        string to_device_name;
        string message;
    }

    event GroupCreation(
        string master_name
    );

    event DeviceAssociation(
        string master_name,
        string device_name
    );

    event MessageTransaction(
        string message_id,
        string from_device_name,
        string to_device_name
    );

    // MAPPING CONTAINTING ALL GROUP DETAILS, CAN ONLY BE ACCESSED BY GROUP MEMBERS 
    mapping(string => group_info) private groups;

    // MAPPING CONTAINING ALL DEVICE DETAILS, CAN BE ACCESSED BY AYONE WHO KNOWS DEVICE NAME
    mapping(string => device_info) public devices;

    // MAPPING CONTAINING ALL MESSAGE DETAILS, 
    // CAN BE ACCESSED BY ANYONE WHOKNOW THE MESSAGE-NO AND IS AUTHENTIC MEMBER OF GROUP
    // MESSAGE CONFIDENTIALITY IS LEFT TO SENDER-RECIVER CRYPTO CHOICE
    mapping(string => message_info) private messages;

    // FUNCTION TO CHECK IF GROUP ALREADY EXIXTS
    function groupExists(string memory secret_key) public view returns (bool){
        return (groups[secret_key].exist);
    }

    // FUNCTION TO CHECK IF DEVICE IS A FOLLOWER OF GROUP
    function followerExists(
        string memory secret_key,
        string memory _device_name
    )public view returns (uint256){
        if(
            groupExists(secret_key) 
            && devices[_device_name].exist
        ){
            for(uint i=0; i<groups[secret_key].followers.length; i++){
                if(keccak256(bytes(groups[secret_key].followers[i])) == keccak256(bytes(_device_name)))
                    return i+1;
            }
            return 0;
        }
        return 0;
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
        uint8 follower_count
    ) public payable returns(bool) {

        if(!groupExists(secret_key) && msg.value>=10**18){

            //transfer funds 
            deploy_wallet.transfer(msg.value);
            
            // creating master device
            device_info memory master;
            master.exist = true;
            master.device_name = master_name;
            master.public_key = master_public_key;
            master.previous_keys = new string[](0);
            master.public_address = master_public_address;
            master.master = true;
            master.future_master = true;

            // adding master as new device
            devices[master_name] = master;
            emit DeviceAssociation(master_name, master_name);
            // }

            // creating/adding the new group
            groups[secret_key] = group_info({
                exist: true,
                owner: msg.sender,
                master_device: devices[master_name],
                masters: new string[](0),
                max_size: follower_count,
                tokens: (msg.value/10**18)*1000-5,
                followers: new string[](0)
            });

            groups[secret_key].followers.push(master_name);
            groups[secret_key].masters.push(master_name);
            emit GroupCreation(master_name);

            return true;
        }
        return false;
    }

    // FUNCTION TO REMOVE GROUP
    function removeGroup(string memory secret_key) public returns (bool){

        if (groupExists(secret_key)){
            devices[groups[secret_key].master_device.device_name].master = false;
            delete groups[secret_key];
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
        bool _future_master
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
                previous_keys: new string[](0),
                public_address: _public_address,
                master: false,
                future_master: _future_master
            });
            devices[_device_name].previous_keys.push(_public_key);
            groups[secret_key].followers.push(_device_name);
            groups[secret_key].tokens -= 1;
            emit DeviceAssociation(groups[secret_key].master_device.device_name,_device_name);
            
            return (true);
        }

        // if group and device exists ... check if device already in group 
        else if(
            devices[_device_name].exist
            && groupExists(secret_key)
        ){
            // check if public key is same
            if(keccak256(bytes(devices[_device_name].public_key)) == keccak256(bytes(_public_key))){
                
                if(followerExists(secret_key,_device_name)>0)
                    return true;

                // if device not in group add it. Enables single device multiple group
                groups[secret_key].followers.push(_device_name);
                emit DeviceAssociation(groups[secret_key].master_device.device_name,_device_name);
                return true;
            }
            // if public key is different archive it
            // this is marked to change : to check of public key update
            else{
                devices[_device_name].public_key = _public_key;
                devices[_device_name].previous_keys.push(_public_key);
                // check in group here?
            }
            
        }

        return false;
    }

    // FUNCTION TO REMOVE A DEVICE FROM GROUP, token cost 1
    function removeDevice(
        string memory secret_key,
        string memory _device_name
    )public returns (bool){
        
        uint256 position = followerExists(secret_key,_device_name);
        // check if device is part of group
        if(position>0){
            uint256 index = position-1;
            // check if index is correct
            if(index>=0 && index<groups[secret_key].followers.length){
                for (uint i=index; i<(groups[secret_key].followers.length-1) ; i++){
                    groups[secret_key].followers[i] = groups[secret_key].followers[i+1];
                }
                delete groups[secret_key].followers[groups[secret_key].followers.length-1];
                // groups[secret_key].followers.length--;
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
    ) public returns (bool){

        if (
            groupExists(secret_key) &&
            devices[_device_name].exist &&
            // cannot be master of two groups !
            !devices[_device_name].master &&
            devices[_device_name].future_master
        ){

            if(followerExists(secret_key,_device_name)>0){
                groups[secret_key].master_device = devices[_device_name];
                groups[secret_key].tokens -= 1;
                // remove master from followers as .... master is only replaced if and only if master dies.
                removeDevice(secret_key,_device_name);
                return true;
            }

        }
        return false;
    }

    // FUNCTION TO CHECK IF MESSAGE EXIXTS
    function messageExist(string memory message_id) public view returns (bool){
        return (messages[message_id].exist);
    }

    // FUNCITON TO ADD MESSAGE, token cost 1
    function addMessage(
        string memory secret_key,
        string memory from_device_name,
        string memory to_device_name,
        string memory message_id,
        string memory data_message
    )public returns (bool){
        
        // check if group exists and both devices are authentic members
        if(
            groupExists(secret_key) 
            && followerExists(secret_key, to_device_name)>0
            && followerExists(secret_key, from_device_name)>0
            && !messageExist(message_id)
        ){
            // create a new message
            message_info memory new_message;
            new_message.exist = true;
            new_message.from_device_name = from_device_name;
            new_message.to_device_name = to_device_name;
            new_message.message = data_message;

            // add message and collect token fee
            messages[message_id] = new_message;
            groups[secret_key].tokens -= 1;

            // emit event here
            emit MessageTransaction(message_id, from_device_name, to_device_name);

            return true;
        }
        return false;
    }

    // FUNCTION TO RETRIEVE ADDED MESSAGE DATA
    function retrieveMessageData(
        string memory secret_key,
        string memory _device_name,
        string memory _message_id
    )public view returns (string memory){

        if(
            groupExists(secret_key) &&
            followerExists(secret_key, _device_name)>0 &&
            messageExist(_message_id) &&
            keccak256(bytes(messages[_message_id].to_device_name)) == keccak256(bytes(_device_name))
        ){
            return messages[_message_id].message;
        }
        return '';
    }

    // FUNCTION TO RETRIEVE ADDED MESSAGE FROM DEVICE NAME
    function retrieveMessageFromDevice(
        string memory secret_key,
        string memory _device_name,
        string memory _message_id
    )public view returns (string memory){

        if(
            groupExists(secret_key) &&
            followerExists(secret_key, _device_name)>0 &&
            messageExist(_message_id) &&
            keccak256(bytes(messages[_message_id].to_device_name)) == keccak256(bytes(_device_name))
        ){
            return messages[_message_id].from_device_name;
        }
        return '';
    }
}