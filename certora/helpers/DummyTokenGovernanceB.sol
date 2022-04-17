// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12;               // HARNESS: ^ -> >=

import "../../node_modules/@bancor/token-governance/contracts/TokenGovernance.sol";

contract DummyTokenGovernanceB is TokenGovernance {
    constructor(IMintableToken mintableToken) TokenGovernance(mintableToken)  {}
}
