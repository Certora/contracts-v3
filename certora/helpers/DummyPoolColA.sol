// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.13;

import "../munged/pools/PoolCollection.sol";

contract DummyPoolColA is PoolCollection {
    constructor(
        IBancorNetwork initNetwork,
        IERC20 initBNT,
        INetworkSettings initNetworkSettings,
        IMasterVault initMasterVault,
        IBNTPool initBNTPool,
        IExternalProtectionVault initExternalProtectionVault,
        IPoolTokenFactory initPoolTokenFactory,
        IPoolMigrator initPoolMigrator
    ) PoolCollection(initNetwork, initBNT, initNetworkSettings,
    initMasterVault, initBNTPool, initExternalProtectionVault, 
    initPoolTokenFactory, initPoolMigrator) {
    }

}
