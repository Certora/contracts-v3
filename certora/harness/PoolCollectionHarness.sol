// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/pools/PoolCollection.sol";

contract PoolCollectionHarness is PoolCollection{
   using EnumerableSet for EnumerableSet.AddressSet;
   using TokenLibrary for Token;
   
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

    //  function tradeBySource(
    //      bytes32 contextId,
    //      Token sourceToken,
    //      Token targetToken,
    //      uint256 sourceAmount,
    //      uint256 minReturnAmount
    //  ) public returns (uint256,uint256,uint256) {
    //      TradeAmountAndFee memory result = tradeBySourceAmount(contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    //      return (result.amount, result.tradingFeeAmount, result.networkFeeAmount);
    //  }
    //  function tradeByTarget(
    //      bytes32 contextId,
    //      Token sourceToken,
    //      Token targetToken,
    //      uint256 targetAmount,
    //      uint256 maxSourceAmount
    //  ) public returns (uint256,uint256,uint256) {
    //      TradeAmountAndFee memory result = tradeByTargetAmount(contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);
    //      return (result.amount, result.tradingFeeAmount, result.networkFeeAmount);
    // }


       function depositFor(
        bytes32 contextId,
        address provider,
        Token pool,
        uint256 tokenAmount
    ) public override returns (uint256) {
        pool.safeTransferFrom(msg.sender, address(_masterVault) , tokenAmount);
        return super.depositFor(contextId, msg.sender, pool, tokenAmount);
    }
    function getPoolDataTradingEnabled(Token pool) public view returns (bool) {
        // Pool storage data = _poolStorage(pool);
        return _poolData[pool].tradingEnabled;
    }
    function getPoolDataBaseTokenLiquidity(Token pool) public view returns (uint128) {
        // Pool storage data = _poolStorage(pool);
        return _poolData[pool].liquidity.baseTokenTradingLiquidity;
    }
    function getPoolDataBntTradingLiquidity(Token pool) public view returns (uint128) {
        // Pool storage data = _poolStorage(pool);
        return _poolData[pool].liquidity.bntTradingLiquidity;
    }
    function getPoolDataStakedBalance(Token pool) public view returns (uint256) {
        // Pool storage data = _poolStorage(pool);
        return _poolData[pool].liquidity.stakedBalance;
    }
     function getPoolDataTotalSupply(Token pool) public view returns (uint256) {
         //Pool storage data = _poolStorage(pool);
         return _poolData[pool].poolToken.totalSupply();
     }
     function getPoolDataAverageRateN(Token pool) public view returns (uint256) {
         //Pool storage data = _poolStorage(pool);
         return _poolData[pool].averageRate.rate.n;
     }
     function getPoolDataAverageRateD(Token pool) public view returns (uint256) {
         //Pool storage data = _poolStorage(pool);
         return _poolData[pool].averageRate.rate.d;
     }
    
    function getPoolDataTradingFee(Token pool) public view returns (uint32) {
        // Pool storage data = _poolStorage(pool);
        return _poolData[pool].tradingFeePPM;
    }
    function getPoolTokenTotalSupply(IPoolToken poolToken) external view returns (uint256) {
        return poolToken.totalSupply();
    }
    function hasPool(Token pool) public view returns (bool) {
        return _pools.contains(address(pool));
    }
    function tokenUserBalance(Token pool, address user)  external view returns (uint256){
            return pool.balanceOf(user);
    }
    function poolWithdrawalAmounts(Token pool,uint256 poolTokenAmount) 
        external view returns (uint){
            InternalWithdrawalAmounts memory amounts = 
            _poolWithdrawalAmounts(pool,_poolData[pool],poolTokenAmount);
            return amounts.baseTokensToTransferFromMasterVault;
    }

    function isPoolStable(Token pool) external view returns (bool)
    {
        PoolLiquidity memory prevLiquidity = _poolData[pool].liquidity;
        AverageRate memory averageRate = _poolData[pool].averageRate;
        return _poolRateState(prevLiquidity, averageRate) == PoolRateState.Stable;
    }

    function isPoolUnstable(Token pool) external view returns (bool)
    {
        PoolLiquidity memory prevLiquidity = _poolData[pool].liquidity;
        AverageRate memory averageRate = _poolData[pool].averageRate;
        return _poolRateState(prevLiquidity, averageRate) == PoolRateState.Unstable;
    }
    
    // function poolTotalSupply(Token pool) external view returns (uint) {
    //     return _poolData[pool].poolToken.totalSupply();
    // }

        // function callRemoveTokenFromWhiteList(Token token) external {
        //     networkSettings.removeTokenFromWhitelist(token);
        // }

}
