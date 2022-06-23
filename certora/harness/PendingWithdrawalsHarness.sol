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
    
    function poolTotalSupply(IPoolToken poolToken) external view returns (uint256) {
        return poolToken.totalSupply();
    }
    
    function poolTokenBalance(IPoolToken poolToken, address account) external view 
    returns (uint256) {
        return poolToken.balanceOf(account);
    }

    // Added a getter (also made the variable public, see contract)
    function nextWithdrawalRequestId() external view returns (uint256){
        return _nextWithdrawalRequestId;
    }
        
}
