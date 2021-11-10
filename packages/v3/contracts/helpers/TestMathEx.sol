// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.9;
pragma abicoder v2;

import { MathEx, Uint512 } from "../utility/MathEx.sol";
import { Fraction } from "../utility/Types.sol";

contract TestMathEx {
    function floorSqrt(uint256 num) external pure returns (uint256) {
        return MathEx.floorSqrt(num);
    }

    function ceilSqrt(uint256 num) external pure returns (uint256) {
        return MathEx.ceilSqrt(num);
    }

    function productRatio(Fraction memory x, Fraction memory y) external pure returns (Fraction memory) {
        return MathEx.productRatio(x, y);
    }

    function reducedRatio(Fraction memory r, uint256 max) external pure returns (Fraction memory) {
        return MathEx.reducedRatio(r, max);
    }

    function normalizedRatio(Fraction memory r, uint256 scale) external pure returns (Fraction memory) {
        return MathEx.normalizedRatio(r, scale);
    }

    function accurateRatio(Fraction memory r, uint256 scale) external pure returns (Fraction memory) {
        return MathEx.accurateRatio(r, scale);
    }

    function roundDiv(uint256 n, uint256 d) external pure returns (uint256) {
        return MathEx.roundDiv(n, d);
    }

    function mulDivF(
        uint256 x,
        uint256 y,
        uint256 z
    ) external pure returns (uint256) {
        return MathEx.mulDivF(x, y, z);
    }

    function mulDivC(
        uint256 x,
        uint256 y,
        uint256 z
    ) external pure returns (uint256) {
        return MathEx.mulDivC(x, y, z);
    }

    function subMax0(uint256 n1, uint256 n2) external pure returns (uint256) {
        return MathEx.subMax0(n1, n2);
    }

    function mul512(uint256 x, uint256 y) external pure returns (Uint512 memory) {
        return MathEx.mul512(x, y);
    }

    function gt512(Uint512 memory x, Uint512 memory y) external pure returns (bool) {
        return MathEx.gt512(x, y);
    }

    function lt512(Uint512 memory x, Uint512 memory y) external pure returns (bool) {
        return MathEx.lt512(x, y);
    }

    function gte512(Uint512 memory x, Uint512 memory y) external pure returns (bool) {
        return MathEx.gte512(x, y);
    }

    function lte512(Uint512 memory x, Uint512 memory y) external pure returns (bool) {
        return MathEx.lte512(x, y);
    }
}
