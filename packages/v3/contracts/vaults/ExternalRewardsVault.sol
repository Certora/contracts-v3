// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.9;

import { ReserveToken } from "../token/ReserveToken.sol";

import { Vault } from "./Vault.sol";
import { IExternalRewardsVault } from "./interfaces/IExternalRewardsVault.sol";
import { IVault } from "./interfaces/IVault.sol";

/**
 * @dev External Rewards Vault contract
 */
contract ExternalRewardsVault is IExternalRewardsVault, Vault {
    // the asset manager role is required to access all the reserves
    bytes32 public constant ROLE_ASSET_MANAGER = keccak256("ROLE_ASSET_MANAGER");

    // upgrade forward-compatibility storage gap
    uint256[MAX_GAP - 0] private __gap;

    /**
     * @dev fully initializes the contract and its parents
     */
    function initialize() external initializer {
        __ExternalRewardsVault_init();
    }

    // solhint-disable func-name-mixedcase

    /**
     * @dev initializes the contract and its parents
     */
    function __ExternalRewardsVault_init() internal initializer {
        __Vault_init();

        __ExternalRewardsVault_init_unchained();
    }

    /**
     * @dev performs contract-specific initialization
     */
    function __ExternalRewardsVault_init_unchained() internal initializer {
        // set up administrative roles
        _setRoleAdmin(ROLE_ASSET_MANAGER, ROLE_ADMIN);

        // allow the deployer to initially manage the assets of the contract
        _setupRole(ROLE_ASSET_MANAGER, msg.sender);
    }

    /**
     * @dev returns the current version of the contract
     */
    function version() external pure override returns (uint16) {
        return 1;
    }

    /**
     * @inheritdoc Vault
     */
    function isPayable() public pure override(IVault, Vault) returns (bool) {
        return true;
    }

    /**
     * @dev authenticate the right of a caller to withdraw a specific amount of a token to a target
     *
     * requirements:
     *
     * - the caller must have the ROLE_ASSET_MANAGER permission
     */
    function authenticateWithdrawal(
        address caller,
        ReserveToken, /* reserveToken */
        address, /* target */
        uint256 /* amount */
    ) internal view override returns (bool) {
        return hasRole(ROLE_ASSET_MANAGER, caller);
    }
}
