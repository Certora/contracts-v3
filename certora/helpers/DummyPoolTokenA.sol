// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/pools/PoolToken.sol";

/**
 * @dev Pool Token contract
 */
contract DummyPoolTokenA is PoolToken {
   
    constructor(
        string memory name,
        string memory symbol,
        uint8 initDecimals,
        Token initReserveToken
    ) PoolToken(name, symbol, initDecimals, initReserveToken) { }
    // ERC20(name, symbol) ERC20Permit(name) validAddress(address(initReserveToken))
}
