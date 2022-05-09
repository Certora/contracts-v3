// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import { PPM_RESOLUTION as M } from "../munged/utility/Constants.sol";
import { Sint256, Uint512, MathEx } from "../munged/utility/MathEx.sol";

error PoolCollectionWithdrawalInputInvalid();

library PoolCollectionWithdrawal {
    using MathEx for uint256;

    struct Output {
        Sint256 p;
        Sint256 q;
        Sint256 r;
        uint256 s;
        uint256 t;
        uint256 u;
        uint256 v;
    }

    function requireValues(uint256 a,uint256 b,uint256 c,
    uint256 w, uint256 m,uint256 n) internal pure {
        require (
            a == 291_762_234_165_599_000_000_000 &&  // a
            b == 216_553_090_379_207_000_000 && // b
            c == 21_681_452_129_588_000_000 && // c
            w == 0 && // w
            m == 2000 && // m
            n == 2500 // n
        );
    }

    function getSTUV(uint256 a,uint256 b,uint256 c,
        uint256 e, uint256 w, uint256 m, uint256 n, uint256 x) 
        public pure returns(uint256,uint256,uint256,uint256){
            Output memory output = 
            calculateWithdrawalAmounts(a,b,c,e,w,m,n,x);
            return (output.s,output.t,output.u,output.v);
    }

    function getPQR(uint256 a,uint256 b,uint256 c,
        uint256 e, uint256 w, uint256 m, uint256 n, uint256 x) 
        public pure 
        returns(uint256 p, uint256 q, uint256 r){
            Output memory output = 
            calculateWithdrawalAmounts(a,b,c,e,w,m,n,x);
            p = output.p.value;
            q = output.q.value;
            r = output.r.value;
    }

    function calculateWithdrawalAmounts(
        uint256 a, // <= 2**128-1
        uint256 b, // <= 2**128-1
        uint256 c, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 w, // <= 2**128-1
        uint256 m, // <= M == 1000000
        uint256 n, // <= M == 1000000
        uint256 x /// <= e <= 2**128-1
    ) internal pure returns (Output memory output) {
        // given the restrictions above, everything below can be declared `unchecked`

        requireValues(a,b,c,w,m,n);

        if (
            a > type(uint128).max ||
            b > type(uint128).max ||
            c > type(uint128).max ||
            e > type(uint128).max ||
            w > type(uint128).max ||
            m > M ||
            n > M ||
            x > e
        ) {
            revert PoolCollectionWithdrawalInputInvalid();
        }

        require((e * (M - n)) / M > b + c); // deficit

        uint256 y = (x * (M - n)) / M;

        // We currently assume that the pool is always in deficit
        // so ((e * (M - n)) / M > b + c) == true

        uint256 f = (e * (M - n)) / M - (b + c);
        uint256 g = e - (b + c);

        // The affordableDeficit function inlined
        Uint512 memory lhs = MathEx.mul512(b * e, f * m + e * n);
        Uint512 memory rhs = MathEx.mul512(f * x, g * (M - m));
        // require we are in the first case in the if statement
        require(b * x < c * (e - x) && MathEx.gt512(lhs, rhs)); 

        // The arbitrageDeficit function inline
        output = arbitrageDeficit(a, b, e, f, m, x, y);

        output.v = x - y;
    }

    function arbitrageDeficit(
        uint256 a, // <= 2**128-1
        uint256 b, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 f, // == e*(1-n)-b-c <= e <= 2**128-1
        uint256 m, // <= M == 1000000
        uint256 x, // <= e <= 2**128-1
        uint256 y /// == x*(1-n) <= x <= e <= 2**128-1
    ) private pure returns (Output memory output) {
        // given the restrictions above, everything below can be declared `unchecked`
        uint256 i = f * (M - m);
        uint256 j = mulSubMulDivF(b, e * M, x, i, 1);
        output.p = MathEx.mulDivF(a * x, i, j).toPos256();
        output.r = MathEx.mulDivF(x, f, e).toNeg256();
        output.s = y;
    }

     /**
     * @dev returns `a*b-x*y/z`
     */
    function mulSubMulDivF(
        uint256 a,
        uint256 b,
        uint256 x,
        uint256 y,
        uint256 z
    ) internal pure returns (uint256) {
        return a * b - MathEx.mulDivF(x, y, z);
    }
}