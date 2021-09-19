// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.7.6;
pragma abicoder v2;

import { IVersioned } from "../../utility/interfaces/IVersioned.sol";
import { Fraction } from "../../utility/Types.sol";

import { IReserveToken } from "../../token/interfaces/IReserveToken.sol";

import { INetworkSettings } from "../../network/interfaces/INetworkSettings.sol";
import { IBancorNetwork } from "../../network/interfaces/IBancorNetwork.sol";

import { AverageRate } from "../PoolAverageRate.sol";

import { IPoolToken } from "./IPoolToken.sol";
import { IPoolTokenFactory } from "./IPoolTokenFactory.sol";

struct PoolLiquidity {
    uint256 networkTokenTradingLiquidity; // the network token trading liquidity
    uint256 baseTokenTradingLiquidity; // the base token trading liquidity
    uint256 tradingLiquidityProduct; // the product of the base token and network token trading liquidities (used for fee calculations)
    uint256 stakedBalance; // the staked balance
}

struct Pool {
    IPoolToken poolToken; // the pool token of a given pool
    uint32 tradingFeePPM; // the trading fee (in units of PPM)
    bool tradingEnabled; // whether trading is enabled
    bool depositingEnabled; // whether depositing is enabled
    AverageRate averageRate; // the recent average rate
    Fraction initialRate; // the initial rate of one base token in network token units in a given pool
    uint256 depositLimit; // the deposit limit
    PoolLiquidity liquidity; // the overall liquidity in the pool
}

// base toke deposit output amounts
struct DepositAmounts {
    uint256 networkTokenDeltaAmount; // the network token amount that was added to the trading liquidity
    uint256 baseTokenDeltaAmount; // the base token amount that was added to the trading liquidity
    uint256 poolTokenAmount; // the minted pool token amount
    IPoolToken poolToken; // the pool token
}

// base token withdrawal output amounts
struct WithdrawalAmounts {
    uint256 baseTokenAmountToTransferFromVaultToProvider; // the base token amount to transfer from the vault to the provider
    uint256 networkTokenAmountToMintForProvider; // the network token amount to mint directly for the provider
    uint256 baseTokenAmountToTransferFromExternalProtectionWalletToProvider; // the base token amount to transfer from the external protection wallet to the provider
    uint256 baseTokenAmountToDeductFromLiquidity; // the base token amount to deduct from the trading liquidity
    uint256 networkTokenAmountToDeductFromLiquidity; // the network token amount to deduct from the trading liquidity and burn in the vault
    uint256 baseTokenWithdrawalFeeAmount; // the base token amount to keep in the pool as a withdrawal fee
    int256 networkTokenArbitrageAmount; // the network token amount to burn or mint in the pool, in order to create an arbitrage incentive
}

/**
 * @dev Pool Collection interface
 */
interface IPoolCollection is IVersioned {
    /**
     * @dev returns the type of the pool
     */
    function poolType() external pure returns (uint16);

    /**
     * @dev returns the network contract
     */
    function network() external view returns (IBancorNetwork);

    /**
     * @dev returns the network settings contract
     */
    function settings() external view returns (INetworkSettings);

    /**
     * @dev returns the pool token factory contract
     */
    function poolTokenFactory() external view returns (IPoolTokenFactory);

    /**
     * @dev returns the default trading fee (in units of PPM)
     */
    function defaultTradingFeePPM() external view returns (uint32);

    /**
     * @dev returns all the pools which are managed by this pool collection
     */
    function pools() external view returns (IReserveToken[] memory);

    /**
     * @dev returns the number of all the pools which are managed by this pool collection
     */
    function poolCount() external view returns (uint256);

    /**
     * @dev returns whether a pool is valid
     */
    function isPoolValid(IReserveToken reserveToken) external view returns (bool);

    /**
     * @dev returns whether a pool's rate is stable
     */
    function isPoolRateStable(IReserveToken reserveToken) external view returns (bool);

    /**
     * @dev returns the overall liquidity in the pool
     */
    function poolLiquidity(IReserveToken reserveToken) external view returns (PoolLiquidity memory);

    /**
     * @dev creates a new pool
     *
     * requirements:
     *
     * - the caller must be the network contract
     * - the pool should have been whitelisted
     * - the pool isn't already defined in the collection
     */
    function createPool(IReserveToken reserveToken) external;

    /**
     * @dev deposits base token liquidity on behalf of a specific provider
     *
     * requirements:
     *
     * - the caller must be the network contract
     * - assumes that the base token has been already deposited in the vault
     */
    function depositFor(
        address provider,
        IReserveToken pool,
        uint256 baseTokenAmount,
        uint256 unallocatedNetworkTokenLiquidity
    ) external returns (DepositAmounts memory);

    /**
     * @dev handles some of the withdrawal-related actions and returns all of the withdrawal-related amounts
     *
     * requirements:
     *
     * - the caller must be the network contract
     * - the caller must have approved the collection to transfer/burn the pool token amount on its behal
     */
    function withdraw(
        IReserveToken pool,
        uint256 basePoolTokenAmount,
        uint256 baseTokenVaultBalance,
        uint256 externalProtectionWalletBalance
    ) external returns (WithdrawalAmounts memory);
}
