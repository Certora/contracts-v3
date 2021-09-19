// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.7.6;

import { IOwned } from "./interfaces/IOwned.sol";

/**
 * @dev this contract provides support and utilities for contract ownership
 */
abstract contract Owned is IOwned {
    address private _owner;
    address private _newOwner;

    /**
     * @dev triggered when the owner is updated
     */
    event OwnerUpdate(address indexed prevOwner, address indexed newOwner);

    // solhint-disable func-name-mixedcase

    /**
     * @dev initializes the contract
     */
    constructor() {
        _setOwner(msg.sender);
    }

    // solhint-enable func-name-mixedcase

    // allows execution by the owner only
    modifier onlyOwner() {
        _onlyOwner();

        _;
    }

    // error message binary size optimization
    function _onlyOwner() private view {
        require(msg.sender == _owner, "ERR_ACCESS_DENIED");
    }

    /**
     * @inheritdoc IOwned
     */
    function owner() public view virtual override returns (address) {
        return _owner;
    }

    /**
     * @inheritdoc IOwned
     */
    function transferOwnership(address ownerCandidate) public virtual override onlyOwner {
        require(ownerCandidate != _owner, "ERR_SAME_OWNER");

        _newOwner = ownerCandidate;
    }

    /**
     * @inheritdoc IOwned
     */
    function acceptOwnership() public virtual override {
        require(msg.sender == _newOwner, "ERR_ACCESS_DENIED");

        _setOwner(_newOwner);
    }

    /**
     * @dev returns the address of the new owner candidate
     */
    function newOwner() external view returns (address) {
        return _newOwner;
    }

    /**
     * @dev sets the new owner internally
     */
    function _setOwner(address ownerCandidate) private {
        address prevOwner = _owner;

        _owner = ownerCandidate;
        _newOwner = address(0);

        emit OwnerUpdate({ prevOwner: prevOwner, newOwner: ownerCandidate });
    }
}
