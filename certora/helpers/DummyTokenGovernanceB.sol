// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;        

import "../munged/helpers/TestTokenGovernance.sol";

contract DummyTokenGovernanceB is TestTokenGovernance {
    constructor(IMintableToken mintableToken) TestTokenGovernance(mintableToken) {}

    function getBNTBalance(address account) public view returns (uint256) {
        return _token.balanceOf(account);
    }

}