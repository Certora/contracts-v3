// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.9;

import "../pools/PoolCollectionFormulas/ThresholdFormula.sol";

contract TestThresholdFormula {
    function surplus(
        uint256 b,
        uint256 c,
        uint256 e,
        uint256 m,
        uint256 n,
        uint256 x
    ) external pure returns (bool) {
        return ThresholdFormula.surplus(b, c, e, m, n, x);
    }

    function deficit(
        uint256 b,
        uint256 c,
        uint256 e,
        uint256 m,
        uint256 n,
        uint256 x
    ) external pure returns (bool) {
        return ThresholdFormula.deficit(b, c, e, m, n, x);
    }
}