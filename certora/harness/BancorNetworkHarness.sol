// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/network/BancorNetwork.sol";

/**
 * @dev Bancor Network contract
 */
contract BancorNetworkHarness is BancorNetwork {
    constructor(
        ITokenGovernance initBNTGovernance,
        ITokenGovernance initVBNTGovernance,
        INetworkSettings initNetworkSettings,
        IMasterVault initMasterVault,
        IExternalProtectionVault initExternalProtectionVault,
        IPoolToken initBNTPoolToken
    ) BancorNetwork(
            initBNTGovernance, 
            initVBNTGovernance, 
            initNetworkSettings, 
            initMasterVault, 
            initExternalProtectionVault, 
            initBNTPoolToken
    ) {}

    function ethBalance() public view returns(uint256){
        return address(this).balance;
    }
}
