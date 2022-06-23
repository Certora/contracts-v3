// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/pools/PoolCollection.sol";
import "../munged/utility/FractionLibrary.sol";


contract PoolCollectionHarness is PoolCollection{
   using EnumerableSet for EnumerableSet.AddressSet;
   using TokenLibrary for Token;
   
   using FractionLibrary for Fraction112;
   
    constructor(
        IBancorNetwork initNetwork,
        IERC20 initBNT,
        INetworkSettings initNetworkSettings,
        IMasterVault initMasterVault,
        IBNTPool initBNTPool,
        IExternalProtectionVault initExternalProtectionVault,
        IPoolTokenFactory initPoolTokenFactory,
        IPoolMigrator initPoolMigrator,
        uint32 initNetworkFeePPM
    ) PoolCollection(initNetwork, initBNT, initNetworkSettings, initMasterVault, initBNTPool, initExternalProtectionVault, initPoolTokenFactory, initPoolMigrator, initNetworkFeePPM) {}

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
        return _poolData[pool].tradingEnabled;
    }
    function getPoolDataBaseTokenLiquidity(Token pool) public view returns (uint128) {
        return _poolData[pool].liquidity.baseTokenTradingLiquidity;
    }
    function getPoolDataBntTradingLiquidity(Token pool) public view returns (uint128) {
        return _poolData[pool].liquidity.bntTradingLiquidity;
    }
    function getPoolDataStakedBalance(Token pool) public view returns (uint256) {
        return _poolData[pool].liquidity.stakedBalance;
    }
     function getPoolDataTotalSupply(Token pool) public view returns (uint256) {
         return _poolData[pool].poolToken.totalSupply();
     }
     function getPoolDataAverageRateN(Token pool) public view returns (uint256) {
         return _poolData[pool].averageRates.rate.n;
     }
     function getPoolDataAverageRateD(Token pool) public view returns (uint256) {
         return _poolData[pool].averageRates.rate.d;
     }
    
    function getPoolDataTradingFee(Token pool) public view returns (uint32) {
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

    // uint256 baseTokensWithdrawalAmount;
    // PoolLiquidity memory liquidity;
    // uint32 poolTradingFeePPM;
    // uint256 poolTokenTotalSupply;
    // function poolWithdrawalAmounts(Token pool,uint256 poolTokenAmount) 
    //     external view returns (uint){
    //         InternalWithdrawalAmounts memory amounts = 
    //         _poolWithdrawalAmounts(pool,_poolData[pool],poolTokenAmount, baseTokensWithdrawalAmount, liquidity, poolTradingFeePPM, poolTokenTotalSupply);
    //         return amounts.baseTokensToTransferFromMasterVault;
    // }

    function isPoolStable(Token pool) external override view returns (bool)
    {
        PoolLiquidity memory prevLiquidity = _poolData[pool].liquidity;
        AverageRates memory averageRate = _poolData[pool].averageRates;
        return _poolRateState(prevLiquidity, averageRate) == PoolRateState.Stable;
    }

    function isPoolUnstable(Token pool) external view returns (bool)
    {
        PoolLiquidity memory prevLiquidity = _poolData[pool].liquidity;
        AverageRates memory averageRate = _poolData[pool].averageRates;
        return _poolRateState(prevLiquidity, averageRate) == PoolRateState.Unstable;
    }
    
    function averageRateIsPositive(Token pool) public view returns (bool) {
        AverageRates memory averageRateInfo = _poolData[pool].averageRates;
        Fraction112 memory averageRate = averageRateInfo.rate;
        return averageRate.isPositive();
     }
}
