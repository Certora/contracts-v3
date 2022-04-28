// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/pools/PoolCollection.sol";

contract PoolCollectionHarness is PoolCollection{
   
    constructor(
        IBancorNetwork initNetwork,
        IERC20 initBNT,
        INetworkSettings initNetworkSettings,
        IMasterVault initMasterVault,
        IBNTPool initBNTPool,
        IExternalProtectionVault initExternalProtectionVault,
        IPoolTokenFactory initPoolTokenFactory,
        IPoolMigrator initPoolMigrator
    ) PoolCollection(initNetwork, initBNT, initNetworkSettings, initMasterVault, initBNTPool, initExternalProtectionVault, initPoolTokenFactory, initPoolMigrator) {}
/*
    function tradeBySourcePoolCollectionT(
        // IPoolCollection poolCollection,
        bytes32 contextId,
        Token sourceToken,
        Token targetToken,
        uint256 sourceAmount,
        uint256 minReturnAmount
    ) public returns (uint256,uint256,uint256) {
        TradeAmountAndFee memory result = tradeBySourceAmount(contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
        return (result.amount, result.tradingFeeAmount, result.networkFeeAmount);
    }
*/
    // Added getters for stakedBalance and total supply
    function poolStakedBalance(Token pool) external view returns (uint) {
        return _poolData[pool].liquidity.stakedBalance;
    }

    function poolTotalSupply(Token pool) external view returns (uint) {
        return _poolData[pool].poolToken.totalSupply();
    }
}
