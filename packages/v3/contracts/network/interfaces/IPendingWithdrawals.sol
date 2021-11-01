// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.9;
pragma abicoder v2;

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import { IPoolToken } from "../../pools/interfaces/IPoolToken.sol";
import { INetworkTokenPool } from "../../pools/interfaces/INetworkTokenPool.sol";

import { ReserveToken } from "../../token/ReserveToken.sol";

import { IUpgradeable } from "../../utility/interfaces/IUpgradeable.sol";

import { INetworkSettings } from "./INetworkSettings.sol";
import { IBancorNetwork } from "./IBancorNetwork.sol";

/**
 * @dev the data struct representing a pending withdrawal request
 */
struct WithdrawalRequest {
    address provider; // the liquidity provider
    IPoolToken poolToken; // the locked pool token
    ReserveToken reserveToken; // the reserve token to withdraw
    uint32 createdAt; // the time when the request was created (Unix timestamp))
    uint256 poolTokenAmount; // the locked pool token amount
    uint256 reserveTokenAmount; // the expected reserve token amount to withdraw
}

/**
 * @dev the data struct representing a completed withdrawal request
 */
struct CompletedWithdrawal {
    IPoolToken poolToken; // the transferred pool token
    uint256 poolTokenAmount; // the transferred pool token amount
}

/**
 * @dev Pending Withdrawals interface
 */
interface IPendingWithdrawals is IUpgradeable {
    /**
     * @dev returns the network contract
     */
    function network() external view returns (IBancorNetwork);

    /**
     * @dev returns the network token contract
     */
    function networkToken() external view returns (IERC20);

    /**
     * @dev returns the network token pool contract
     */
    function networkTokenPool() external view returns (INetworkTokenPool);

    /**
     * @dev returns the lock duration
     */
    function lockDuration() external view returns (uint32);

    /**
     * @dev returns withdrawal window duration
     */
    function withdrawalWindowDuration() external view returns (uint32);

    /**
     * @dev returns the pending withdrawal requests count for a specific provider
     */
    function withdrawalRequestCount(address provider) external view returns (uint256);

    /**
     * @dev returns the pending withdrawal requests IDs for a specific provider
     */
    function withdrawalRequestIds(address provider) external view returns (uint256[] memory);

    /**
     * @dev returns the pending withdrawal request with the specified ID
     */
    function withdrawalRequest(uint256 id) external view returns (WithdrawalRequest memory);

    /**
     * @dev initiates liquidity withdrawal
     *
     * requirements:
     *
     * - the caller must have approved the contract to transfer the pool token amount on its behalf
     */
    function initWithdrawal(IPoolToken poolToken, uint256 poolTokenAmount) external;

    /**
     * @dev initiates liquidity withdrawal by providing an EIP712 typed signature for an EIP2612 permit request
     *
     * requirements:
     *
     * - the caller must have provided a valid and unused EIP712 typed signature
     */
    function initWithdrawalPermitted(
        IPoolToken poolToken,
        uint256 poolTokenAmount,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    /**
     * @dev returns whether the given request is ready for withdrawal
     */
    function readyForWithdrawal(uint256 id) external view returns (bool);

    /**
     * @dev cancels a withdrawal request
     *
     * requirements:
     *
     * - the caller must have already initiated a withdrawal and received the specified id
     */
    function cancelWithdrawal(uint256 id) external;

    /**
     * @dev reinitiates a withdrawal request and restarts its cooldown durations
     *
     * requirements:
     *
     * - the caller must have already initiated a withdrawal and received the specified id
     */
    function reinitWithdrawal(uint256 id) external;

    /**
     * @dev completes a withdrawal request and returns the pool token and its transferred amount
     *
     * requirements:
     *
     * - the caller must be the network contract
     * - the provider must have already initiated a withdrawal and received the specified id
     * - the current time is older than the lock duration but not older than the lock duration + withdrawal window duration
     */
    function completeWithdrawal(
        bytes32 contextId,
        address provider,
        uint256 id
    ) external returns (CompletedWithdrawal memory);
}
