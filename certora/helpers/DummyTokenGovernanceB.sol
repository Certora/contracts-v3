// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;        

import "contracts/helpers/TestTokenGovernance.sol";

contract DummyTokenGovernanceB is TestTokenGovernance {
    constructor(IMintableToken mintableToken) TestTokenGovernance(mintableToken) {}
}