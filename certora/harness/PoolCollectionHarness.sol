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

    function tradeBySource(
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
    function tradeByTarget(
        bytes32 contextId,
        Token sourceToken,
        Token targetToken,
        uint256 targetAmount,
        uint256 maxSourceAmount
    ) public returns (uint256,uint256,uint256) {
        TradeAmountAndFee memory result = tradeBySourceAmount(contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);
        return (result.amount, result.tradingFeeAmount, result.networkFeeAmount);
    }

    function getPoolDataTradingEnabled(Token pool) public view returns (bool) {
        Pool storage data = _poolStorage(pool);
        return data.tradingEnabled;
    }
    function getPoolDataBaseTokenLiquidity(Token pool) public view returns (uint128) {
        Pool storage data = _poolStorage(pool);
        return data.liquidity.baseTokenTradingLiquidity;
    }
    function getPoolDataBntTradingLiquidity(Token pool) public view returns (uint128) {
        Pool storage data = _poolStorage(pool);
        return data.liquidity.bntTradingLiquidity;
    }
    function getPoolDataStakedBalance(Token pool) public view returns (uint256) {
        Pool storage data = _poolStorage(pool);
        return data.liquidity.stakedBalance;
    }
    
}
