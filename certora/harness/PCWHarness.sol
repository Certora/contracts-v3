// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import { PPM_RESOLUTION as M } from "../munged/utility/Constants.sol";
import { Sint256, Uint512, MathEx } from "../munged/utility/MathEx.sol";

library PoolCollectionWithdrawal
{
    struct Output {
        Sint256 p;
        Sint256 q;
        Sint256 r;
        uint256 s;
        uint256 t;
        uint256 u;
        uint256 v;
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
    ) internal pure returns (Output memory output){
        
         require ((e * (M - n)) / M > b + c, "Only deficit");

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
             revert ("Invalid");
         }

         uint256 f = (e * (M - n)) / M - (b + c);
         uint256 g = e - (b + c);

         if(isStable(b, c, e, x) && affordableDeficit(b, e, f, g, m, n, x)){
             output = arbitrageDeficit(a,b,c,e,w,m,n,x);
         }
         else if(a>0){
             output = defaultDeficit(a,b,c,e,w,m,n,x);
         }
         else{
             uint256 y = (x * (M - n)) / M;
             output.s = (y * c) / e;
             (output.t, output.u) = externalProtection(a, b, e, g, y, w);
         }
    }

    function arbitrageDeficit(
        uint256 a, // <= 2**128-1
        uint256 b, // <= 2**128-1
        uint256 c, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 w, // <= 2**128-1
        uint256 m, // <= M == 1000000
        uint256 n, // <= M == 1000000
        uint256 x /// <= e <= 2**128-1
    ) internal pure returns (Output memory output) {
        uint256 y = (x * (M - n)) / M;
        output.s = y;
        output.t = 0;
        output.u = 0;
        output.v = x - y;
        output.r.value == output.s - x*(b+c)/e;
        output.r.isNeg == true;
        output.p.value = output.r.value*a*(M-m)/(b*M-output.r.value*(M-m));
        output.p.isNeg == false;
        output.q.value = 0;
    }

    function defaultDeficit(
        uint256 a, // <= 2**128-1
        uint256 b, // <= 2**128-1
        uint256 c, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 w, // <= 2**128-1
        uint256 m, // <= M == 1000000
        uint256 n, // <= M == 1000000
        uint256 x /// <= e <= 2**128-1
    ) internal pure returns (Output memory output) {
        uint256 y = (x * (M - n)) / M;
        output.s = y * (b+c)/e;
        output.t = a*(x*(M-n)/M-output.s)/b;
        if(w==0){
            output.u = 0;
        }
        else{
            output.u = (x * (M-n)/M * (e - b - c))/e - output.t*b/a;
        }
        output.v = x - y;
        output.r.value ==  MathEx.subMax0(y * b, c * (e - y))/e ;
        output.r.isNeg == true;
        output.p.value = output.r.value*a*(M-m)/(b*M-output.r.value*(M-m));
        output.p.isNeg == true;
        output.q = output.p;
    }

    function affordableDeficit(
        uint256 b, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 f, // == e*(1-n)-b-c <= e <= 2**128-1
        uint256 g, // == e-b-c <= e <= 2**128-1
        uint256 m, // <= M == 1000000
        uint256 n, // <= M == 1000000
        uint256 x /// <  e*c/(b+c) <= e <= 2**128-1
    ) internal pure returns (bool) {
        // Original code:
            // given the restrictions above, everything below can be declared `unchecked`
            //Uint512 memory lhs = MathEx.mul512(b * e, f * m + e * n);
            //Uint512 memory rhs = MathEx.mul512(f * x, g * (M - m));
            //return MathEx.gt512(lhs, rhs);

        // Simplification (no uint512):
            //uint256 lhs = b * e * (f * m + e * n);
            //uint256 rhs = f * x* g * (M - m) ;
            // return lhs > rhs;

        // Equivalent to :
            // e * b / f * [1 - (M-m)/M * f / (f + e*n)] > x*(M-m)/M
            // A weaker inequality is (implied):
        return e * b > f * x*(M-m)/M;
    }

    function externalProtection(
        uint256 a, // <= 2**128-1
        uint256 b, // <= 2**128-1
        uint256 e, // <= 2**128-1
        uint256 g, // == e-b-c <= e <= 2**128-1
        uint256 y, // == x*(1-n) <= x <= e <= 2**128-1
        uint256 w /// <= 2**128-1
    ) private pure returns (uint256 t, uint256 u) {
        // given the restrictions above, everything below can be declared `unchecked`
        uint256 yg = y * g;
        uint256 we = w * e;
        if (yg > we) {
            t = a > 0 ? MathEx.mulDivF(a, yg - we, b * e) : 0;
            u = w;
        } else {
            t = 0;
            u = yg / e;
        }
    }

    function isStable(uint b,uint c,uint e,uint x)
    internal pure returns(bool) {
        return b * x < c * (e - x);
    }

    function inRange(uint256 base, uint offset, uint256 maxDevPPM)
    external pure returns (bool) {
        uint256 min = base*(M - maxDevPPM);
        uint mid = offset * M;
        uint max = base * (M + maxDevPPM);
        return min<=mid && mid<=max;
    }
}
