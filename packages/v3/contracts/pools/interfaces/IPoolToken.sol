// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.7.6;

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { IERC20Permit } from "@openzeppelin/contracts/drafts/IERC20Permit.sol";

import { IReserveToken } from "../../token/interfaces/IReserveToken.sol";
import { IERC20Burnable } from "../../token/interfaces/IERC20Burnable.sol";

import { IVersioned } from "../../utility/interfaces/IVersioned.sol";
import { IOwned } from "../../utility/interfaces/IOwned.sol";

/**
 * @dev Pool Token interface
 */
interface IPoolToken is IVersioned, IOwned, IERC20, IERC20Permit, IERC20Burnable {
    /**
     * @dev returns the address of the reserve token
     */
    function reserveToken() external view returns (IReserveToken);

    /**
     * @dev increases the token supply and sends the new tokens to the given account
     *
     * requirements:
     *
     * - the caller must be the owner of the contract
     */
    function mint(address recipient, uint256 amount) external;
}
