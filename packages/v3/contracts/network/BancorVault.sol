// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.7.6;

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { SafeERC20 } from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

import { ReentrancyGuardUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";

import { Upgradeable } from "../utility/Upgradeable.sol";
import { Utils } from "../utility/Utils.sol";

import { IReserveToken } from "../token/interfaces/IReserveToken.sol";
import { ReserveToken } from "../token/ReserveToken.sol";

import { IBancorVault } from "./interfaces/IBancorVault.sol";

/**
 * @dev Bancor Vault contract
 */
contract BancorVault is IBancorVault, Upgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable, Utils {
    using SafeERC20 for IERC20;
    using ReserveToken for IReserveToken;

    // the admin role is used to pause/unpause the vault
    bytes32 public constant ROLE_ADMIN = keccak256("ROLE_ADMIN");

    // the asset manager role is required to access all the reserves
    bytes32 public constant ROLE_ASSET_MANAGER = keccak256("ROLE_ASSET_MANAGER");

    // the asset manager role is only required to access the network token reserve
    bytes32 public constant ROLE_NETWORK_TOKEN_MANAGER = keccak256("ROLE_NETWORK_TOKEN_MANAGER");

    // the address of the network token
    IERC20 private immutable _networkToken;

    // upgrade forward-compatibility storage gap
    uint256[MAX_GAP - 0] private __gap;

    /**
     * @dev triggered when tokens have been withdrawn from the vault
     */
    event TokensWithdrawn(IReserveToken indexed token, address indexed caller, address indexed target, uint256 amount);

    /**
     * @dev a "virtual" constructor that is only used to set immutable state variables
     */
    constructor(IERC20 networkToken) validAddress(address(networkToken)) {
        _networkToken = networkToken;
    }

    /**
     * @dev fully initializes the contract and its parents
     */
    function initialize() external initializer {
        __BancorVault_init();
    }

    // solhint-disable func-name-mixedcase

    /**
     * @dev initializes the contract and its parents
     */
    function __BancorVault_init() internal initializer {
        __Upgradeable_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        __BancorVault_init_unchained();
    }

    /**
     * @dev performs contract-specific initialization
     */
    function __BancorVault_init_unchained() internal initializer {
        // set up administrative roles
        _setRoleAdmin(ROLE_ADMIN, ROLE_ADMIN);
        _setRoleAdmin(ROLE_ASSET_MANAGER, ROLE_ASSET_MANAGER);
        _setRoleAdmin(ROLE_NETWORK_TOKEN_MANAGER, ROLE_ASSET_MANAGER);

        // allow the deployer to initially govern the contract
        _setupRole(ROLE_ADMIN, msg.sender);
        _setupRole(ROLE_ASSET_MANAGER, msg.sender);
    }

    // solhint-enable func-name-mixedcase

    modifier onlyAdmin() {
        _hasRole(ROLE_ADMIN, msg.sender);

        _;
    }

    receive() external payable override {}

    /**
     * @dev returns the current version of the contract
     */
    function version() external pure override returns (uint16) {
        return 1;
    }

    /**
     * @inheritdoc IBancorVault
     */
    function isPaused() external view override returns (bool) {
        return paused();
    }

    /**
     * @inheritdoc IBancorVault
     */
    function pause() external override onlyAdmin {
        _pause();
    }

    /**
     * @inheritdoc IBancorVault
     */
    function unpause() external override onlyAdmin {
        _unpause();
    }

    /**
     * @inheritdoc IBancorVault
     */
    function withdrawTokens(
        IReserveToken reserveToken,
        address payable target,
        uint256 amount
    ) external override validAddress(target) nonReentrant whenNotPaused {
        require(
            (address(reserveToken) == address(_networkToken) && hasRole(ROLE_NETWORK_TOKEN_MANAGER, msg.sender)) ||
                hasRole(ROLE_ASSET_MANAGER, msg.sender),
            "ERR_ACCESS_DENIED"
        );

        reserveToken.safeTransfer(target, amount);

        emit TokensWithdrawn({ token: reserveToken, caller: msg.sender, target: target, amount: amount });
    }
}
