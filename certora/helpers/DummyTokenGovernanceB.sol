// SPDX-License-Identifier: MIT
pragma solidity 0.8.13;              // HARNESS: ^ -> >=

//import "../../node_modules/@bancor/token-governance/contracts/TokenGovernance.sol";
import "contracts/helpers/TestTokenGovernance.sol";
contract DummyTokenGovernanceB is TestTokenGovernance {
    constructor(IMintableToken mintableToken) TestTokenGovernance(mintableToken) {}
}