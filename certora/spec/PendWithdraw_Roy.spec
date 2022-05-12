import "../helpers/erc20.spec"

using BancorNetwork as BN
using BNTPool as BNTp
using PoolCollectionHarness as PC
using DummyPoolTokenA as ptA
using DummyPoolTokenB as ptB
using DummyERC20A as erc20
using PendingWithdrawalsHarness as MAIN

/* *************************
LAST SANITY CHECK (rule_sanity basic) 28/04 :
https://vaas-stg.certora.com/output/41958/f3e175bb27d0b6b5e87d/?anonymousKey=6a8e0fc0949d1287e8824f1ab4b814c20cd3361a
*****************************/

methods {
    nextWithdrawalRequestId() returns(uint256) envfree
    withdrawalRequestCount(address) envfree
    lockDuration() returns(uint32) envfree
    _bntPool() returns(address) envfree
    poolTotalSupply(address) returns (uint256) envfree
    withdrawalRequest(uint256) returns ((address, address, address, uint32,uint256,uint256)) envfree
    poolTokenBalance(address,address) returns(uint256) envfree
    completeWithdrawal(bytes32,address,uint256)
    initWithdrawal(address,address,uint256) 
    returnToken(address) returns(address) envfree
    poolValidity(address) returns(bool) envfree
    withdrawalRequestSpecificId(address, uint) returns uint envfree
    // Bancor Network
    collectionByPool(address) returns(address) => DISPATCHER(true)
    // BNT Pool
    poolTokenToUnderlying(uint256) returns(uint256) => DISPATCHER(true)
    // Pool collection
    poolTokenToUnderlying(address, uint256) returns(uint256) => DISPATCHER(true)
    isPoolValid(address) returns(bool) => DISPATCHER(true)
    // Pool token
    reserveToken() returns (address) => DISPATCHER(true)
    // ERC20 Burnable
    burn(uint256) => DISPATCHER(true)
}

//////////////////////////////////////
/*
  *********** Ghosts & Hooks ********
*/
//////////////////////////////////////

// The sum of balances for some token
//ghost sumOfBalances(address token) returns uint256{
//    init_state axiom forall address token. sumOfBalances(token) ==0;
//}

// Total pool tokens in registerd requests
ghost sumRequestPoolTokens(address) returns uint256 {
    init_state axiom forall address PT. sumRequestPoolTokens(PT) == 0;
}

// Ghost for a provider of a request (id)
ghost requestProviderGhost(uint) returns address {
    init_state axiom forall uint id. requestProviderGhost(id) == 0;
}

// Ghost for a pool token of a request (id)
ghost requestPoolTokenGhost(uint) returns address {
    init_state axiom forall uint id. requestPoolTokenGhost(id) == 0;
}

// Hook to havoc the pool token of request (id)
hook Sstore _withdrawalRequests[KEY uint256 id].poolToken address PT STORAGE {
    havoc requestPoolTokenGhost assuming forall uint256 id2.
    id2 == id => requestPoolTokenGhost@new(id2) == PT;
}

// Hook to havoc the provider of request (id)
hook Sstore _withdrawalRequests[KEY uint256 id].provider address Provider STORAGE {
    havoc requestProviderGhost assuming forall uint256 id2.
    id == id2 => requestProviderGhost@new(id2) == Provider;
}

// Hook to havoc the total number of pool tokens registered in requests.
hook Sstore _withdrawalRequests[KEY uint256 id].poolTokenAmount uint256 balance (uint256 old_balance) STORAGE {
    require requestPoolTokenGhost(id) !=0;
    havoc sumRequestPoolTokens assuming forall address poolToken.
    ((requestPoolTokenGhost(id) == poolToken) ?
    sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken) + balance - old_balance :
    sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken));
}

// A preconditioner for a valid request.
// @note : Probably requires additions (valid pool token address),
// requiring different than zero address might be superfluous.
function ValidRequest(address provider, address poolToken,
    address reserveToken, uint256 poolTokenAmount)
   {
       require (
            provider != 0 && provider != poolToken && 
            provider != reserveToken &&
            (poolToken == ptA || poolToken == ptB) &&
            reserveToken == erc20);
   }
// Preconditioner for valid index of provider requests array.
function ValidInd_Request(address provider, uint ind) returns bool
{
    return ind < withdrawalRequestCount(provider);
}
// Number of pool tokens in withdrawal request.
function RequestPoolTokensAmount(uint id) returns uint256 {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return poolTokenAmount;
}
// Provider of withdrawal request.
function RequestProvider(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return provider;
}
// Pool token total supply in withdrawal request.
function RequestPoolTokenTotalSupply(uint id) returns uint256 {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return MAIN.poolTotalSupply(poolToken);
}
// ReserveToken in withdrawal request.
function RequestReserveToken(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    return reserveToken;
}
// Pool token in withdrawal request.
function RequestPoolToken(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    return poolToken;
}
// Summarization for mulDivF (currently not in use)
function mulDivNoFloorSummary(uint256 x,uint256 y,uint256 z) returns uint256 {
  require(z >0);
  uint256 w = (x * y) / z;
  require w*z == x*y;
  return x;
}
// Remainder of multiplication by division
function MulMod(uint x, uint y, uint z) returns uint256 {
    require z>0;
    return to_uint256(x*y) % z;
}
// Purpose: to bound the product x*y from overflowing (xy<2^256-1)
function noProdOverFlow(uint x, uint y){
     uint bound = to_uint256(2^128-1);
     require x <= bound && y <= bound;
}

////////////////////////////////////
/*
    ********** RULES ***************
*/
////////////////////////////////////
// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (BNTPool impl.)
// Current status: PASSES*
// *For the product terms x,y we require x,y < 2^128-1.
rule poolTokenToUnderlyingMono_BNT(uint256 amount1,uint256 amount2)
{
    env e;
    address token = erc20;
    uint TotalSupply = MAIN.poolTotalSupply(BNTp.poolToken(e));
    uint stake = BNTp.stakedBalance(e);

    require TotalSupply > 0 && stake > 0;
    noProdOverFlow(stake,amount1);
    noProdOverFlow(stake,amount2);

    uint UAmount1 = BNTp.poolTokenToUnderlying(e,amount1);
    uint UAmount2 = BNTp.poolTokenToUnderlying(e,amount2);

    // Checking for weak monotonicity:
    assert (amount2 > amount1) => (UAmount1 <= UAmount2), "Monotonic decreasing";
    // Checking for strong monotonicity (excluding division remainders):
    assert(
        MulMod(stake,amount1,TotalSupply) ==0 && 
        MulMod(stake,amount2,TotalSupply) ==0 &&
        amount2 > amount1) => (UAmount1 < UAmount2), "Non monotonic increasing";
}

// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (PoolCollection impl.)
// Current status: PASSES*
// *For the product terms x,y we require x,y < 2^128-1.
rule poolTokenToUnderlyingMono_PC(uint256 amount1,uint256 amount2)
{
    env e;
    address token = erc20;
    uint TotalSupply; 
    uint stake = PC.poolStakedBalance(e,token);
    
    require PC.poolToken(e,token) == ptA;
    require TotalSupply > 0 && stake > 0;
    require PC.poolTotalSupply(e,token) == TotalSupply;
    noProdOverFlow(stake,amount1);
    noProdOverFlow(stake,amount2);

    uint UAmount1 = PC.poolTokenToUnderlying(e,token,amount1);
    uint UAmount2 = PC.poolTokenToUnderlying(e,token,amount2);
    
    // Checking for weak monotonicity:
    assert (amount2 > amount1) => (UAmount1 <= UAmount2), "Monotonic decreasing";
    // Checking for strong monotonicity (excluding division remainders):
    assert(
        MulMod(stake,amount1,TotalSupply) ==0 && 
        MulMod(stake,amount2,TotalSupply) ==0 &&
        amount2 > amount1) => (UAmount1 < UAmount2), "Non monotonic increasing";
}

// Unit test for poolTokenToUnderlying in Pool collection
// Current status: PASSES
rule poolTokenToUnderlying_PC_check(uint256 amount, uint stake)
{
    env e;
    address token = erc20;

    require PC.poolToken(e,token) == ptA;
    require PC.poolTotalSupply(e,token) == 1;
    require PC.poolStakedBalance(e,token) == stake;

    uint UAmount = PC.poolTokenToUnderlying(e,token,amount);

    assert UAmount == amount*stake;
}

// Given a previous withdrawal request with id (id),
// no further call to InitWithdrawal can override the previous withdrawal.
// In other words, any new withdrawal request must have a different ID than (id).
// Current status: PASSES
rule InitWithdrawalNoOverride(uint id)
{
    env e;
    address provider; address provider2; 
    address poolToken; address poolToken2;
    address reserveToken; 
    uint32 createdAt; 
    uint256 poolTokenAmount; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount; 
    uint id2;

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    // require that request is valid.
    ValidRequest(provider,poolToken,reserveToken,poolTokenAmount);
    require id < nextWithdrawalRequestId();

    // If initWithdrawal completed successfully, it must not override 
    // the previously defined request.
    id2 = initWithdrawal(e,provider2,poolToken2,poolTokenAmount2);
    assert id2 != id, "New withdrawal was created with the same ID of 
    an existing one";
}

// Init withdrawal must register the details of the request correctly,
// by creating a WithdrawalRequest object in the withdrawalRequest mapping.
// Current status: PASSES
rule initWithdrawalIntegrity()
{
    env e;
    uint id;
    address provider; address providerInit;
    address poolToken; address poolTokenInit; 
    address reserveToken; 
    uint32 createdAt; 
    uint256 poolTokenAmount; uint256 poolTokenAmountInit;
    uint256 reserveTokenAmount; 

    // The initWithdrawal function is a callee from BancorNetwork
    // where the argument is message sender. We can safely assume that 
    // providerInit is a valid non-zero address.
    // If implementation changes, we should check it in BancorNetwork.sol
    require providerInit !=0;

    id = initWithdrawal@withrevert(e,providerInit,poolTokenInit,poolTokenAmountInit);
    bool WithdrawRevert = lastReverted;
    
    assert (poolTokenInit==0 || poolTokenAmountInit==0)
    => WithdrawRevert, "initWithdrawal completed with zero address";

    require !WithdrawRevert;

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    assert (provider == providerInit &&
            poolTokenAmount == poolTokenAmountInit &&
            poolToken == poolTokenInit
            ,"initWithdrawal did not register request as expected");
}

// Withdrawal request cannot be completed more than once.
// Current status: PASSES
rule NoDoubleWithdrawal(bytes32 contID, address provider, uint256 id)
{
    env e;
    completeWithdrawal(e,contID,provider,id);
    completeWithdrawal@withrevert(e,contID,provider,id);
    assert lastReverted, "One cannot be allowed to complete a withdrawal twice";
}

// Withdrawal request cannot be cancelled more than once.
// Current status: PASSES
rule NoDoubleCancellation(address provider, uint256 id)
{
    env e;
    cancelWithdrawal(e,provider,id);
    cancelWithdrawal@withrevert(e,provider,id);
    assert lastReverted, "One cannot be allowed to cancel a withdrawal twice";
}

// initWithdrawal must increase nextWithdrawalRequestId by one.
// If reverts, for any reason, the next ID musn't change.
// Current status: PASSES
rule ChangeNextWithdrawalId()
{
    env e;
    calldataarg args;
    address user;
    address pool;
    uint amount;
    uint id1 = nextWithdrawalRequestId();

    initWithdrawal@withrevert(e,user, pool, amount);

    bool reverted = lastReverted;
    uint id2 = nextWithdrawalRequestId();

    assert !reverted => id1+1 == id2, "id wasn't increased by 1 as expected";
    assert reverted => id1 == id2, "id was changed unexpectedly";
}

// Attempt to use struct in CVL - IGNORE
/*
rule StructWithdrawalRequest(uint id)
{
    MAIN.WithdrawalRequest var;
    address provider;
    env e;
    sinvoke cancelWithdrawal(e,provider, id);
    require var == MAIN.withdrawalRequest(id) ;
    assert var.provider == 0;
}*/
//
// Any cancelled request with a given id, cannot be associated
// with any provider (including the original).
// Current status: PASSES
rule CancelWithdrawalIntegrity(uint id, address pro)
{
    env e;
    address provider1; address provider2;
    address poolToken1; address poolToken2;  
    address reserveToken1; address reserveToken2;
    uint32 createdAt1; uint32 createdAt2; 
    uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount1; uint256 reserveTokenAmount2;

    provider1, poolToken1, reserveToken1, createdAt1, poolTokenAmount1, 
        reserveTokenAmount1 = currentContract.withdrawalRequest(id);
    
    require provider1 == pro;
    cancelWithdrawal(e,provider1, id);
    
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
        reserveTokenAmount2 = currentContract.withdrawalRequest(id);

    assert provider2 == 0, "A cancelled request if associated with some non-zero address";
}

// Checks which functions change nextWithdrawalRequestId
// Current status: PASSES
rule nextWithIDVaries(method f)
{
    env e;
    calldataarg args;

    uint id1 = nextWithdrawalRequestId();
    f(e,args);
    uint id2 = nextWithdrawalRequestId();

    assert id1<=id2, "nextWithdrawalRequestId decreased unexpectedly";
    
    assert ( 
        (id1+1==id2) => 
        f.selector == initWithdrawal(address,address,uint256).selector,
        "Function ${f} changed nextWithdrawalRequestId by 1");
   
    require id1+1 != id2;
    
    assert id1==id2, "nextWithdrawalRequestId changed unexepectedly";
}

// After a successful initWithdrawal request for provider,
// his/hers request count must increase by one.
// Current status: PASSES
rule WithdrawalCountConsistent_Init(address provider)
{
    address pool;
    env e;
    uint amount;
    uint ReqCountBefore = withdrawalRequestCount(provider);
    // Neglecting overflow case
    require ReqCountBefore < max_uint ; 

    initWithdrawal(e,provider, pool, amount);

    uint ReqCountAfter = withdrawalRequestCount(provider);
    assert ReqCountAfter == ReqCountBefore+1;
}

// After a successful cancelWithdrawal request for provider,
// his/hers request count must decrease by one.
// Current status: PASSES
rule WithdrawalCountConsistent_Cancel(address provider, uint id)
{
    env e;
    uint ReqCountBefore = withdrawalRequestCount(provider); 

    cancelWithdrawal(e,provider,id);

    uint ReqCountAfter = withdrawalRequestCount(provider);

    assert ReqCountAfter == ReqCountBefore-1;
}

// The protocol's intention is to prevent withdrawal abuse.
// The rule checks that withdrawal is not possible immediately
// after registering a request.
// Thought: should we use two different envs to prove this rule?
// Current status: PASSES
rule NoImmediateWithrawal(address provider, bytes32 contID)
{
    env e;
    address poolToken;
    uint256 Amount;
    uint id;
    id = initWithdrawal(e,provider,poolToken,Amount);

    require poolToken == ptA;
    // This probably holds all the time. See lockDurationNotZero.
    // In the future, we can replace this by an invariant requirement.
    require lockDuration() > 0; 
    
    assert !isReadyForWithdrawal(e,id),"the function should return it is not
    ready for withdrawal"; 

    completeWithdrawal@withrevert(e,contID,provider,id);

    assert lastReverted, "User managed to withdraw immediately despite
    the lock duration";
}

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

// Once a withdrawal request was registered, it should always
// be possible to cancel it by its provider (without time limitation).
// Current status: PASSES *
// * cancelWithdrawal reverts because safeTransfer call in _cancelWithdrawal reverts.
// One has to make sure that the protocol has enough pool tokens in balance.
// This could be assumed if we are sure that they were given to the protocol in advance.
// _removeWithdrawalRequest may also revert because remove function returns false.
// If one ignores this revert statement, the rule passes.
rule CancellingAlwaysPossible(address provider)
{
    env e;
    address poolToken; 
    address reserveToken = erc20;
    require poolToken == ptA || poolToken == ptB;
    uint256 Amount;
    uint id;

    id = initWithdrawal(e,provider,poolToken,Amount);
    ValidRequest(provider,poolToken,reserveToken,Amount);
    // No restriction upon the request count can lead to overflow,
    // Here the limit is arbitrary.
    require withdrawalRequestCount(provider) < max_uint;
    ///
    // This requirement is necessary that the transfer of pool tokens
    // back to the provider won't revert.
    require poolTokenBalance(poolToken, currentContract) >= Amount;
    // Prevent overflow
    require poolTokenBalance(poolToken, provider) + Amount <= max_uint;
    ///
    cancelWithdrawal@withrevert(e,provider,id);

    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}

// Only provider can ask to withdraw request.
// Current status: PASSES
rule WithdrawByProviderOnly(address provider)
{
    env e;
    address poolToken = ptA; 
    bytes32 contID;
    uint256 Amount; address provider2;
    uint id = initWithdrawal(e,provider,poolToken,Amount);
    completeWithdrawal(e,contID,provider2,id);
    assert provider2 == provider;
}

// Only provider can ask to cancel request.
// Current status: PASSES
rule CancelByProviderOnly(address provider)
{
    env e;
    address poolToken = ptA;
    uint256 Amount; address provider2;
    uint id = initWithdrawal(e,provider,poolToken,Amount);
    cancelWithdrawal(e,provider2,id);
    assert provider2 == provider;
}

// Checks the validity of the request ID getter:
// withdrawalRequestSpecificId(provider,index)
// Current status: PASSES
rule checkSpecificId(address provider)
{
    env e;
    address poolToken;
    uint256 Amount;
    // Count1 is the current number of requests for provider.
    uint Count1 = withdrawalRequestCount(provider);
    require Count1 < 100000; //max_uint-1;
    // Now, adding a request to the end of the list.
    // List should be now Count1+1 items long.
    uint id1 = initWithdrawal(e,provider,poolToken,Amount);
    // Thus, the index Count1+1 must be out of bounds.
    withdrawalRequestSpecificId@withrevert(provider,Count1+1);
    assert lastReverted;
    // Adding another one.
    uint id2 = initWithdrawal(e,provider,poolToken,Amount);
    assert withdrawalRequestCount(provider) == Count1+2,
    " Request count should have increased by two";
    // In total, we added two subsequent requests. Validating that
    // function gets them properly.    
    assert id1 == withdrawalRequestSpecificId@withrevert(provider,Count1);
    assert id2 == withdrawalRequestSpecificId@withrevert(provider,Count1+1);
}

// No two identical IDs for provider
// Current status: FAILS
// Preserved violated for completeWithdrawal.
invariant NoIdenticalIDs(address provider, uint ind1, uint ind2)
    (
        ValidInd_Request(provider,ind1) &&
        ValidInd_Request(provider,ind2) &&
        ind1 != ind2
    ) 
    =>
    (
        withdrawalRequestSpecificId(provider,ind1) != 
        withdrawalRequestSpecificId(provider,ind2)
    )
    
    {
        preserved
        {
            require
                (withdrawalRequestSpecificId(provider,ind1) !=0 &&
                withdrawalRequestSpecificId(provider,ind2) !=0);
        }
    }
    

// Withdrawal request details must not vary but only after
// initialize, cancel or complete a withdrawal.
// Current status : PASSES
rule RequestDetailsInvariance(uint id, method f)
{
    bool ValidFunction = (
        f.selector == cancelWithdrawal(address,uint).selector ||
        f.selector == completeWithdrawal(bytes32,address,uint256).selector ||
        f.selector == initWithdrawal(address,address,uint256).selector);

    env e; calldataarg args;
    address provider; address providerAfter;
    address poolToken; address poolTokenAfter;  
    address reserveToken; address reserveTokenAfter;
    uint32 createdAt; uint32 createdAtAfter; 
    uint256 poolTokenAmount; uint256 poolTokenAmountAfter;
    uint256 reserveTokenAmount; uint256 reserveTokenAmountAfter;
    //
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
    reserveTokenAmount = currentContract.withdrawalRequest(id);
    f(e,args);
    providerAfter, poolTokenAfter, reserveTokenAfter, createdAtAfter,
    poolTokenAmountAfter,reserveTokenAmountAfter =
    currentContract.withdrawalRequest(id);
    //
    assert !(provider == providerAfter &&
        poolToken == poolTokenAfter &&
        reserveToken == reserveTokenAfter &&
        poolTokenAmount == poolTokenAmountAfter &&
        reserveTokenAmount == reserveTokenAmountAfter) => ValidFunction,
        "The details of a withdrawal request changed unexpectedly
        after invoking ${f}";
}

// Pool token withdrawal solvency: 
// For a given pool with pool token (poolToken), the sum of all registered pool tokens
// from all requests, must be less or equal to the total supply of that pool token.
//
// Current status : FAILS
// fails for initWithdrawal*
// * see note inside preserved block
invariant TotalRequestPTlessThanSupply(address poolToken)
   sumRequestPoolTokens(poolToken) <= poolTotalSupply(poolToken)
   {
    preserved initWithdrawal(address provider, address poolToken2, uint256 poolTokenAmount)
    with (env e)
    {
        // In Bancor network, before calling initWithdrawal, the provider transfers its
        // Pool tokens to the _pendingWithdrawal contract, i.e. the protocol.
        require poolToken == poolToken2;
        require poolTokenBalance(poolToken, currentContract) >= poolTokenAmount;
        // If we require invariant of solvency:
        // sum(requests pool tokens) <= sum(user balance) <= Total supply
        // this should probably let the rule pass.
        //sumRequestPoolTokens + poolTokenAmount <= sum(userbalance)
        require poolTotalSupply(poolToken) >= poolTokenAmount;
    }
   }

// All pass
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

// For every request, the number of registered pool tokens cannot be larger
// than the total supply.
// Current status: PASSES
// Preserved block may be too lenient (under-approximation).

// Note : This rule proves the inequality for an individual provider.
// It is not enough for solvency. We want to write a new rule using ghosts -
// the sum of all requests pool token amounts is less or equal to the total supply.
invariant PoolTokenLessThanSupply(uint id)
   RequestPoolTokensAmount(id) <= RequestPoolTokenTotalSupply(id)
   {
       preserved initWithdrawal
       (address provider, address poolToken, uint256 poolTokenAmount) with (env e2)
       {  
           address reserveToken;
           require poolToken == ptA;
           require provider != poolToken && provider != currentContract;
           // This requirement relies on the fact that a provider received enough 
           // pool tokens upon deposit.
           require poolTotalSupply(poolToken) >= poolTokenAmount;
       }

       preserved completeWithdrawal(bytes32 contId,address provider2,uint256 id2) with (env e3)
       {
           uint amount1 = RequestPoolTokensAmount(id);
           uint amount2 = RequestPoolTokensAmount(id2);
           uint sumPT = amount1 + amount2;

           require id != id2;
           require sumPT >= amount1 && sumPT >= amount2;
           require RequestPoolToken(id) == ptA;
           require RequestPoolToken(id2) == ptA;
           require sumPT <= RequestPoolTokenTotalSupply(id);
       }

       preserved
       {
           require RequestPoolToken(id) == ptA;
       }
   }
    
// Any change of status of some request cannot affect another one.
// One can prove this rule also for completeWithdrawal.
// Current status: PASSES (both functions)
rule IndependentRequests(uint id1, uint id2, method f) filtered{f->
f.selector == cancelWithdrawal(address,uint).selector}
//f.selector == completeWithdrawal(bytes32,address,uint256).selector}
{
    env e;
    require id1 != id2;
    address provider1; address provider2;
    address poolToken1; address poolToken2;  
    address reserveToken1; address reserveToken2;
    uint32 createdAt1; uint32 createdAt2; 
    uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount1; uint256 reserveTokenAmount2;
    provider1, poolToken1, reserveToken1, createdAt1, poolTokenAmount1, 
    reserveTokenAmount1 = currentContract.withdrawalRequest(id1);
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
    reserveTokenAmount2 = currentContract.withdrawalRequest(id2);
    // Choose a function:
        cancelWithdrawal(e,provider1,id1);
    // Or:
    //    bytes32 contID;
    //    completeWithdrawal(e,contID,provider1,id1);
    address provider3;
    address poolToken3; 
    address reserveToken3; 
    uint32 createdAt3; 
    uint256 poolTokenAmount3; 
    uint256 reserveTokenAmount3;
    provider3, poolToken3, reserveToken3, createdAt3, poolTokenAmount3, 
    reserveTokenAmount3 = currentContract.withdrawalRequest(id2);
    assert provider2 == provider3 &&
        poolToken2 == poolToken3 &&
        reserveToken2 == reserveToken3 &&
        poolTokenAmount2 == poolTokenAmount3 &&
        reserveTokenAmount2 == reserveTokenAmount3,
        "The details of a different withdrawal request changed unexpectedly
        after invoking ${f} on request id = ${id1}";
}

// A withdrawal request can be registered only if the provider has
// enough pool tokens in the given pool.
// Current status: FAILS*
// *InitWithdrawal is a callee in BancorNetwork, in which the pool tokens are transferred
// from the provider to the protocol.
// Alternatively, we can check that the protocol has enough pool tokens.
// Naturally, the rule would still be violated for the same reason.
rule RequestRegisteredForValidProvider(address provider, uint tokenAmount)
{
    env e;
    address poolToken = ptA;
    uint id = initWithdrawal(e,provider,poolToken,tokenAmount);
    //assert ptA.balanceOf(e,provider) >= tokenAmount;
    assert ptA.balanceOf(e,currentContract) >= tokenAmount;
}

// The protocol should burn the pool tokens it received from the provider
// after the withdrawal request was completed.
// Current status: PASSES*
// * We checked that the protocol loses *AT LEAST* the PTamount. 
// In the current implementation of completeWithdrawal, the protocol
// also transfers PT to the provider. This should be changed in the future.
rule BurnPTsAfterCompleteWithdrawal(uint id)
{
    env e;
    address provider = RequestProvider(id);
    bytes32 contID;
    uint PTamount = RequestPoolTokensAmount(id);

    require RequestPoolToken(id) == ptA;
    require provider != ptA;
    
    uint PTbalance1 = ptA.balanceOf(e,currentContract);

    completeWithdrawal(e,contID,provider,id);

    uint PTbalance2 = ptA.balanceOf(e,currentContract);

    assert PTbalance2 + PTamount <= PTbalance1;
}

// For any provider who completes his/hers withdrawal request,
// his/hers pool token balance must not change.
// Current status : FAILS
// The current implementation of completeWithdrawal transfers PT to the
// provider. We know it should change in the future.
rule PTsInvarianceForProvider(uint id)
{
    env e;
    address provider = RequestProvider(id);
    bytes32 contID;

    require RequestPoolToken(id) == ptA;
    require provider != ptA;
    
    uint PTbalance1 = ptA.balanceOf(e,provider);

    completeWithdrawal(e,contID,provider,id);

    uint PTbalance2 = ptA.balanceOf(e,provider);

    assert PTbalance1 == PTbalance2;
}

// After successfully cancelling a withdrawal, the provider should get
// his/hers pool tokens back.
// Current status: PASSES
rule ProviderGetsPTsBack(uint id)
{
    env e;
    address provider = RequestProvider(id);
    uint amount = RequestPoolTokensAmount(id);

    require RequestPoolToken(id) == ptA;
    require provider != ptA && provider != currentContract;

    uint PTbalance1 = ptA.balanceOf(e,provider);
    
    cancelWithdrawal(e,provider,id);
    
    uint PTbalance2 = ptA.balanceOf(e,provider);

    assert PTbalance1 + amount == PTbalance2;
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
