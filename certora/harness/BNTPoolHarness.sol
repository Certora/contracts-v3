// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/pools/BNTPool.sol";


/**
 * @dev BNT Pool contract
 */
contract BNTPoolHarness is BNTPool {
    constructor(
        IBancorNetwork initNetwork,
        ITokenGovernance initBNTGovernance,
        ITokenGovernance initVBNTGovernance,
        INetworkSettings initNetworkSettings,
        IMasterVault initMasterVault,
        IPoolToken initBNTPoolToken
    )
        BNTPool(initNetwork, initBNTGovernance, initVBNTGovernance, initNetworkSettings, initMasterVault, initBNTPoolToken)
        // Vault(initBNTGovernance, initVBNTGovernance)
        // validAddress(address(initNetwork))
        // validAddress(address(initNetworkSettings))
        // validAddress(address(initMasterVault))
        // validAddress(address(initBNTPoolToken))
    { }

    function withdrawalAmountClean(uint256 bntAmount)
        external
        view
        greaterThanZero(bntAmount)
        returns (uint256)
    {
        return _withdrawalAmounts(bntAmount).bntAmount;
    }

}
