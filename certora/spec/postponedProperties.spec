////////////////////////////////////////////////////
//                   BNTPool                      //
////////////////////////////////////////////////////




////////////////////////////////////////////////////
//                PendingWithdrawals              //
////////////////////////////////////////////////////

/*
In order to prevent protocol abuse, withdrawal requests are locked for a 
certain (non-zero) period of time.
 *****************
Current status:
# _instate :
    FAILS because lockDuration is not initialized in constructor.
# _preserved:
    FAILS after calling setLockDuration(uint32) because there is no
    restriction upon the value. 
*/
invariant lockDurationNotZero(env e)
    lockDuration() > 0
    {
        // Assuming initalize was invoked
        preserved
        {
            initialize(e);
        }
    }


// Attempt to use struct in CVL - IGNORE
rule StructWithdrawalRequest(uint id)
{
    MAIN.WithdrawalRequest var;
    address provider;
    env e;
    sinvoke cancelWithdrawal(e,provider, id);
    require var == MAIN.withdrawalRequest(id) ;
    assert var.provider == 0;
}

// Pool token withdrawal solvency: 
// For a given pool with pool token (poolToken), the sum of all registered pool tokens
// from all requests, must be less or equal to the total supply of that pool token.
//
// Current status : FAILS
// fails for initWithdrawal*
// * see note inside preserved block
// Sasha: now it also fails for completeWithdrawal() because withdrawalRequest cannot be removed because of the bug
// probably better move it to the BancorNetwork

invariant totalRequestPTlessThanSupply(address poolToken)
    sumRequestPoolTokens(poolToken) <= poolTotalSupply(poolToken)
    {
        preserved initWithdrawal(address provider, address poolToken2, uint256 poolTokenAmount) with (env e)
        {
            // In Bancor network, before calling initWithdrawal, the provider transfers its
            // Pool tokens to the _pendingWithdrawal contract, i.e. the protocol.
            require poolToken == poolToken2;
            require poolTokenBalance(poolToken, currentContract) >= poolTokenAmount;
            // If we require invariant of solvency:
            // sum(requests pool tokens) <= sum(user balance) <= Total supply
            // this should probably let the rule pass.
            // sumRequestPoolTokens + poolTokenAmount <= sum(userbalance)   
            require poolTotalSupply(poolToken) >= poolTokenAmount;
        }
    }
   

/// transferred to the BancorNetwork spec
// Once a withdrawal request was registered, it should always
// be possible to cancel it by its provider (without time limitation).
// Current status: PASSES *
// * cancelWithdrawal reverts because safeTransfer call in _cancelWithdrawal reverts.
// One has to make sure that the protocol has enough pool tokens in balance.
// This could be assumed if we are sure that they were given to the protocol in advance.
// _removeWithdrawalRequest may also revert because remove function returns false.
// If one ignores this revert statement, the rule passes.
rule cancellingAlwaysPossible(address provider)
{
    env e;
    address poolToken; 
    address reserveToken = erc20;
    require poolToken == ptA || poolToken == ptB;
    uint256 amount;
    uint id;

    id = initWithdrawal(e, provider, poolToken, amount);
    validRequest(provider, poolToken, reserveToken, amount);
    // No restriction upon the request count can lead to overflow,
    // Here the limit is arbitrary.
    require withdrawalRequestCount(provider) < max_uint;
    ///
    // This requirement is necessary that the transfer of pool tokens
    // back to the provider won't revert.
    require poolTokenBalance(poolToken, currentContract) >= amount;
    // Prevent overflow
    require poolTokenBalance(poolToken, provider) + amount <= max_uint;
    ///
    cancelWithdrawal@withrevert(e, provider, id);

    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}

/// transferred to the BancorNetwork spec
// A withdrawal request can be registered only if the provider has
// enough pool tokens in the given pool.
// Current status: FAILS*
// *InitWithdrawal is a callee in BancorNetwork, in which the pool tokens are transferred
// from the provider to the protocol.
// Alternatively, we can check that the protocol has enough pool tokens.
// Naturally, the rule would still be violated for the same reason.
rule requestRegisteredForValidProvider(address provider, uint tokenAmount)
{
    env e;
    address poolToken = ptA;
    uint id = initWithdrawal(e,provider,poolToken,tokenAmount);
    //assert ptA.balanceOf(e,provider) >= tokenAmount;
    assert ptA.balanceOf(e,currentContract) >= tokenAmount;
}

/// Should transfer to the BancorNetwork spec:
// The protocol should burn the pool tokens it received from the provider
// after the withdrawal request was completed.
// Current status: ?
rule burnPTsAfterCompleteWithdrawal(address provider, uint PTamount)
{
    env e; env e2;
    bytes32 contextId;
    address poolToken = ptA;
    require provider != currentContract;

    uint id = initWithdrawal(e,provider,poolToken,PTamount);

    uint PTbalance1 = poolTokenBalance(poolToken, currentContract);
    uint totSupply1 = poolTotalSupply(poolToken);

    completeWithdrawal(e2,contextId,provider,id);

    uint PTbalance2 = poolTokenBalance(poolToken, currentContract);
    uint totSupply2 = poolTotalSupply(poolToken);

    assert PTbalance2 + PTamount == PTbalance1 , "Protocol did not remove its pool tokens";
    assert totSupply2 + PTamount == totSupply1 , "The number of burnt PTs is incorrect";
}


rule whoChangedTotalSupply(method f)            
filtered { f-> !f.isView}
{
    address poolToken = ptA;
    env e;
    calldataarg args;
    uint totSup1 = poolTotalSupply(poolToken);
    f(e,args);
    uint totSup2 = poolTotalSupply(poolToken);
    assert totSup1 == totSup2;
}


// Reachability
// Current status: FAILS for all functions.
rule reachability(method f)
{   
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}

// Cancel withdrawal reachability
rule reachCancelWithdrawal()
{   
    env e;
    address provider;
    uint id = initWithdrawal(e,provider,ptA,1);
    cancelWithdrawal@withrevert(e,provider,id);
    assert !lastReverted ;
}

rule reachCompleteWithdrawal(uint id)
{   
    env e;
    bytes32 contextId;
    address provider;
    completeWithdrawal(e,contextId,provider,id);
    assert false;
}


////////////////////////////////////////////////////
//                PoolCollection                  //
////////////////////////////////////////////////////





////////////////////////////////////////////////////
//                 BancorNetwork                  //
////////////////////////////////////////////////////