// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/vaults/Vault.sol";


contract VaultHarness is Vault {

    constructor(ITokenGovernance initBNTGovernance, ITokenGovernance initVBNTGovernance) Vault(initBNTGovernance, initVBNTGovernance) {}

}
