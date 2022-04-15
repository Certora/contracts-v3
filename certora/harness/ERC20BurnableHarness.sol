// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/token/ERC20Burnable.sol";

/**
 * @dev this is an adapted clone of the OZ's ERC20Burnable extension which is unfortunately required so that it can be
 * explicitly specified in interfaces via our new IERC20Burnable interface.
 *
 * We have also removed the explicit use of Context and updated the code to our style.
 */
contract ERC20BurnableHarness is ERC20Burnable {
    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) {}
}
