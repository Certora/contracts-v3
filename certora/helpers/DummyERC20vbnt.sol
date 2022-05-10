// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.13;

import "contracts/helpers/TestGovernedToken.sol";

contract DummyERC20vbnt is TestGovernedToken {
    constructor(
        string memory name,
        string memory symbol,
        uint256 totalSupply
    ) TestGovernedToken(name, symbol, totalSupply) {
    }

}
