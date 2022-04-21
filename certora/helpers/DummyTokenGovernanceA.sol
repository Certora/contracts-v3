// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;

import "contracts/helpers/TestTokenGovernance.sol";

contract DummyTokenGovernanceA is TestTokenGovernance {
    constructor(IMintableToken mintableToken) TestTokenGovernance(mintableToken)  {}
}
