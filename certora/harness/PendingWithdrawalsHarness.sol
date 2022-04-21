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

    function nextWithdrawalRequestId() external view returns (uint256){
        return _nextWithdrawalRequestId;
    }

    function poolValidity(Token pool) external view returns (bool) {
        return _network.isPoolValid(pool);
    }

    function Burn(uint amount, IPoolToken poolToken) external {
        return poolToken.burn(amount);
    }

    function createWithdrawalRequest(
        address provider,
        IPoolToken poolToken,
        Token reserveToken,
        uint32 createdAt,
        uint256 poolTokenAmount,
        uint256 reserveTokenAmount
    ) public pure returns (WithdrawalRequest memory) {
        return WithdrawalRequest({
            provider: provider, 
            poolToken: poolToken, 
            reserveToken: reserveToken, 
            createdAt: createdAt, 
            poolTokenAmount: poolTokenAmount, 
            reserveTokenAmount: reserveTokenAmount
        }); 
    }
    

    function completedWithdrawalAmount(CompletedWithdrawal memory compWith) public pure returns (uint){
        return compWith.poolTokenAmount; 
    }
    
    function completedWithdrawalPool(CompletedWithdrawal memory compWith) public pure returns (IPoolToken){
        return compWith.poolToken; 
    }

}
