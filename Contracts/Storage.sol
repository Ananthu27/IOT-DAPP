// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract Storage {

    bool internal busy = false;

    struct device_info {
        string device_name;
        string public_key;
        string public_address;
    }

    struct group_info {
        bool exist;
        device_info master_device;
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

    // FUNCTION TO ADD A NEW GROUP
    function addGroup(
        string memory secret_key,
        string memory master_name,
        string memory master_public_key,
        string memory master_public_address,
        uint256 follower_count
    ) public returns(bool) {

        if(!groupExists(secret_key)){

            device_info memory master;
            master.device_name = master_name;
            master.public_key = master_public_key;
            master.public_address = master_public_address;

            devices[master_name] = master;

            groups[secret_key] = group_info({
                exist: true,
                master_device: master,
                followers: new string[](follower_count)
            });

            return true;
        }
        return false;
    }
}