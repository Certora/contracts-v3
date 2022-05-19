// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

/**
 * @dev this contract abstracts the block timestamp in order to allow for more flexible control in tests
 */
contract Time {
    /**
     * @dev returns the current time
     */
    function _time() public view virtual returns (uint32) {         // HRANESS: internal -> public
        return uint32(block.timestamp);
    }

    function _time256() public view virtual returns (uint256) {         // HRANESS: test function
        return block.timestamp;
    }
}
