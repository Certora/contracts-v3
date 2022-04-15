// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity 0.8.13;

import "../munged/network/PendingWithdrawals.sol";


contract PendingWithdrawalsHarness is PendingWithdrawals {
    
    constructor(
        IBancorNetwork initNetwork,
        IERC20 initBNT,
        IBNTPool initBNTPool
    ) PendingWithdrawals(initNetwork, initBNT, initBNTPool) {}


    function returnToken(IPoolToken poolToken) external view returns (Token) {
        return poolToken.reserveToken();
    }

    function poolValidity(Token pool) external view returns (bool) {
        return _network.isPoolValid(pool);
    }
    
}
