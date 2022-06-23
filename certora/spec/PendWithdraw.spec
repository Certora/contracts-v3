import "../helpers/erc20.spec"

using BancorNetwork as BN
using BNTPool as BNTp
using PoolCollectionHarness as PC
using DummyPoolTokenA as ptA
using DummyPoolTokenB as ptB
using DummyERC20A as erc20
using PendingWithdrawalsHarness as MAIN

/* *************************
LAST SANITY CHECK (rule_sanity basic) 22/05 :
https://vaas-stg.certora.com/output/41958/4d0f98faa692c1f5aa89/?anonymousKey=cbe100110510822f35ed4e26731aa4a42fee86a6
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
    withdrawalRequestSpecificId(address, uint) returns uint envfree
    PC.getPoolDataStakedBalance(address) returns (uint) envfree

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
    havoc sumRequestPoolTokens assuming forall address poolToken.
        ((requestPoolTokenGhost(id) == poolToken) ?
        sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken) + balance - old_balance :
        sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken));
}

// A preconditioner for a valid request.
// @note : Probably requires additions (valid pool token address),
// requiring different than zero address might be superfluous.
function validRequest(address provider, address poolToken,
    address reserveToken, uint256 poolTokenAmount)
   {
       require (
            provider != 0 && provider != poolToken && 
            provider != reserveToken &&
            (poolToken == ptA || poolToken == ptB) &&
            reserveToken == erc20);
   }

// Preconditioner for valid index of provider requests array.
function validInd_Request(address provider, uint ind) returns bool
{
    return ind < withdrawalRequestCount(provider);
}

// Number of pool tokens in withdrawal request.
function requestPoolTokensAmount(uint id) returns uint256 {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return poolTokenAmount;
}

// Provider of withdrawal request.
function requestProvider(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return provider;
}

// Pool token total supply in withdrawal request.
function requestPoolTokenTotalSupply(uint id) returns uint256 {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);
    
    return poolTotalSupply(poolToken);
}

// ReserveToken in withdrawal request.
function requestReserveToken(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;
    
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    return reserveToken;
}

// Pool token in withdrawal request.
function requestPoolToken(uint id) returns address {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    return poolToken;
}


function requestCreatedAt(uint id) returns uint32 {
    address provider; address poolToken; address reserveToken;
    uint32 createdAt; uint256 poolTokenAmount; uint256 reserveTokenAmount;

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(id);

    return createdAt;
}

// Remainder of multiplication by division
function mulMod(uint x, uint y, uint z) returns uint256 {
    require z > 0;
    return to_uint256(x * y) % z;
}


////////////////////////////////////
/*
    ********** RULES ***************
*/
////////////////////////////////////
// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (BNTPool impl.)
// Current status: PASSES
rule poolTokenToUnderlyingMono_BNT(uint256 amount1, uint256 amount2)
{
    env e;
    address token = erc20;
    uint TotalSupply = poolTotalSupply(BNTp.poolToken(e));
    uint stake = BNTp.stakedBalance(e);

    require TotalSupply > 0 && stake > 0;

    uint UAmount1 = BNTp.poolTokenToUnderlying(e, amount1);
    uint UAmount2 = BNTp.poolTokenToUnderlying(e, amount2);

    // Checking for weak monotonicity:
    assert (amount2 > amount1) => (UAmount1 <= UAmount2), "Monotonic decreasing";
    // Checking for strong monotonicity (excluding division remainders):
    assert(
        mulMod(stake, amount1, TotalSupply) == 0 && 
        mulMod(stake, amount2, TotalSupply) == 0 &&
        amount2 > amount1) => (UAmount1 < UAmount2), "Non monotonic increasing";
}


// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (PoolCollection impl.)
// Current status: PASSES
 rule poolTokenToUnderlyingMono_PC(uint256 amount1,uint256 amount2)
 {
     env e;
     address token = erc20;
     uint TotalSupply; 
     uint stake = PC.getPoolDataStakedBalance(token);
    
     require PC.poolToken(e, token) == ptA;
     require TotalSupply > 0 && stake > 0;
     require poolTotalSupply(ptA) == TotalSupply;

     uint UAmount1 = PC.poolTokenToUnderlying(e, token, amount1);
     uint UAmount2 = PC.poolTokenToUnderlying(e, token, amount2);
    
     // Checking for weak monotonicity:
     assert (amount2 > amount1) => (UAmount1 <= UAmount2), "Monotonic decreasing";
     // Checking for strong monotonicity (excluding division remainders):
     assert(
         mulMod(stake, amount1, TotalSupply) == 0 && 
         mulMod(stake, amount2, TotalSupply) == 0 &&
         amount2 > amount1) => (UAmount1 < UAmount2), "Non monotonic increasing";
 }

// Unit test for poolTokenToUnderlying in Pool collection
// Current status: PASSES
rule poolTokenToUnderlying_PC_check(uint256 amount, uint stake)
{
    env e;
    address token = erc20;

    require PC.poolToken(e, token) == ptA;
    require poolTotalSupply(ptA) == 1;
    require PC.getPoolDataStakedBalance(token) == stake;

    uint UAmount = PC.poolTokenToUnderlying(e, token, amount);

    assert UAmount == amount * stake;
}

// Given a previous withdrawal request with id (id),
// no further call to InitWithdrawal can override the previous withdrawal.
// In other words, any new withdrawal request must have a different ID than (id).
// Current status: PASSES
rule initWithdrawalNoOverride(uint id)
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
    validRequest(provider, poolToken, reserveToken, poolTokenAmount);
    require id < nextWithdrawalRequestId();

    // If initWithdrawal completed successfully, it must not override 
    // the previously defined request.
    id2 = initWithdrawal(e, provider2, poolToken2, poolTokenAmount2);
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
    require providerInit != 0;

    id = initWithdrawal@withrevert(e, providerInit, poolTokenInit, poolTokenAmountInit);
    bool withdrawRevert = lastReverted;
    
    assert (poolTokenInit == 0 || poolTokenAmountInit == 0)
    => withdrawRevert, "initWithdrawal completed with zero address";

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = withdrawalRequest(id);

    assert !withdrawRevert => 
                    (provider == providerInit &&
                    poolTokenAmount == poolTokenAmountInit &&
                    poolToken == poolTokenInit)
                    ,"initWithdrawal did not register request as expected";
}

// Withdrawal request cannot be completed more than once.
// Current status: PASSES
rule noDoubleWithdrawal(bytes32 contID, address provider, uint256 id)
{
    env e;
    completeWithdrawal(e, contID, provider, id);
    completeWithdrawal@withrevert(e, contID, provider, id);
    assert lastReverted, "One cannot be allowed to complete a withdrawal twice";
}

// Withdrawal request cannot be cancelled more than once.
// Current status: PASSES
rule noDoubleCancellation(address provider, uint256 id)
{
    env e;
    cancelWithdrawal(e,provider,id);
    cancelWithdrawal@withrevert(e,provider,id);
    assert lastReverted, "One cannot be allowed to cancel a withdrawal twice";
}

// initWithdrawal must increase nextWithdrawalRequestId by one.
// If reverts, for any reason, the next ID musn't change.
// Current status: PASSES
rule changeNextWithdrawalId()
{
    env e;
    address user;
    address pool;
    uint amount;
    uint id1 = nextWithdrawalRequestId();

    initWithdrawal@withrevert(e,user, pool, amount);

    bool reverted = lastReverted;
    uint id2 = nextWithdrawalRequestId();

    assert !reverted => id1 + 1 == id2, "id wasn't increased by 1 as expected";
    assert reverted => id1 == id2, "id was changed unexpectedly";
}

// Any cancelled request with a given id, cannot be associated
// with any provider (including the original).
// Current status: PASSES
rule cancelWithdrawalIntegrity(uint id, address pro)
{
    env e;
    address provider1; address provider2;
    address poolToken1; address poolToken2;  
    address reserveToken1; address reserveToken2;
    uint32 createdAt1; uint32 createdAt2; 
    uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount1; uint256 reserveTokenAmount2;

    provider1, poolToken1, reserveToken1, createdAt1, poolTokenAmount1, 
        reserveTokenAmount1 = withdrawalRequest(id);
    
    require provider1 == pro;
    cancelWithdrawal(e, provider1, id);
    
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
        reserveTokenAmount2 = withdrawalRequest(id);

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

    assert id1 <= id2, "nextWithdrawalRequestId decreased unexpectedly";
    
    assert ( 
        (id1 + 1 == id2) => 
        f.selector == initWithdrawal(address,address,uint256).selector,
        "Function ${f} changed nextWithdrawalRequestId by 1");
   
    require id1 + 1 != id2;
    
    assert id1 == id2, "nextWithdrawalRequestId changed unexepectedly";
}

// After a successful initWithdrawal request for provider,
// his/hers request count must increase by one.
// Current status: PASSES
rule withdrawalCountConsistent_Init(address provider)
{
    address pool;
    env e;
    uint amount;
    uint ReqCountBefore = withdrawalRequestCount(provider);
    // Neglecting overflow case
    require ReqCountBefore < max_uint ; 

    initWithdrawal(e,provider, pool, amount);

    uint ReqCountAfter = withdrawalRequestCount(provider);
    assert ReqCountAfter == ReqCountBefore + 1;
}

// After a successful cancelWithdrawal request for provider,
// his/hers request count must decrease by one.
// Current status: PASSES
rule withdrawalCountConsistent_Cancel(address provider, uint id)
{
    env e;
    uint ReqCountBefore = withdrawalRequestCount(provider); 

    cancelWithdrawal(e,provider,id);

    uint ReqCountAfter = withdrawalRequestCount(provider);

    assert ReqCountAfter == ReqCountBefore - 1;
}

// The protocol's intention is to prevent withdrawal abuse.
// The rule checks that withdrawal is not possible immediately
// after registering a request.
// Thought: should we use two different envs to prove this rule?
// Current status: PASSES
rule noImmediateWithrawal(address provider, bytes32 contID)
{
    env e;
    address poolToken;
    uint256 Amount;
    uint id;
    id = initWithdrawal(e, provider, poolToken, Amount);

    require poolToken == ptA;
    // This probably holds all the time. See lockDurationNotZero.
    // In the future, we can replace this by an invariant requirement.
    require lockDuration() > 0; 
    
    assert !isReadyForWithdrawal(e, id),"the function should return it is not
    ready for withdrawal"; 

    completeWithdrawal@withrevert(e, contID, provider, id);

    assert lastReverted, "User managed to withdraw immediately despite
    the lock duration";
}


// Only provider can ask to withdraw request.
// Current status: PASSES
rule withdrawByProviderOnly(address provider)
{
    env e;
    address poolToken = ptA; 
    bytes32 contID;
    uint256 amount; address provider2;
    uint id = initWithdrawal(e, provider, poolToken, amount);
    completeWithdrawal(e, contID, provider2, id);
    assert provider2 == provider;
}

// Only provider can ask to cancel request.
// Current status: PASSES
rule cancelByProviderOnly(address provider)
{
    env e;
    address poolToken = ptA;
    uint256 Amount; address provider2;
    uint id = initWithdrawal(e, provider, poolToken, Amount);
    cancelWithdrawal(e,provider2, id);
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
// Current status: FAILS (cannot understand counter example: https://vaas-stg.certora.com/output/3106/5a3f0e0557d9c474543d/?anonymousKey=e5bda5cae74ec0a61c62a10e145fcbc8c619d4bb) 
// probably issue becuase of disabled deletion from map
invariant noIdenticalIDs(address provider, uint ind1, uint ind2)
    (
        validInd_Request(provider, ind1) &&
        validInd_Request(provider, ind2) &&
        ind1 != ind2
    ) 
    =>
    (
        withdrawalRequestSpecificId(provider, ind1) != 
        withdrawalRequestSpecificId(provider, ind2)
    )
    
    {
        preserved
        {
            require (withdrawalRequestSpecificId(provider, ind1) != 0 &&
                        withdrawalRequestSpecificId(provider, ind2) != 0);
        }
    }
    

// Withdrawal request details must not vary but only after
// initialize, cancel or complete a withdrawal.
// Current status : PASSES
rule requestDetailsInvariance(uint id, method f)
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

// For every request, the number of registered pool tokens cannot be larger
// than the total supply.
// Current status: PASSES
// Preserved block may be too lenient (under-approximation).

// Note : This rule proves the inequality for an individual provider.
// It is not enough for solvency. We want to write a new rule using ghosts -
// the sum of all requests pool token amounts is less or equal to the total supply.
invariant poolTokenLessThanSupply(uint id)
   requestPoolTokensAmount(id) <= requestPoolTokenTotalSupply(id)
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
           uint amount1 = requestPoolTokensAmount(id);
           uint amount2 = requestPoolTokensAmount(id2);
           uint sumPT = amount1 + amount2;

           require id != id2;
           require sumPT >= amount1 && sumPT >= amount2;
           require requestPoolToken(id) == ptA;
           require requestPoolToken(id2) == ptA;
           require sumPT <= requestPoolTokenTotalSupply(id);
       }

       preserved
       {
           require requestPoolToken(id) == ptA;
       }
   }
    


function bothHelper(env e, method f, address provider1, bytes32 contID, uint id1) {
    if (f.selector == cancelWithdrawal(address,uint).selector) {
        cancelWithdrawal(e, provider1, id1);
    } else {    // f.selector == completeWithdrawal(bytes32,address,uint256).selector
        completeWithdrawal(e, contID, provider1, id1);
    }
}


// Any change of status of some request cannot affect another one.
// One can prove this rule also for completeWithdrawal.
// Current status: PASSES (both functions)
rule independentRequests(env e, method f) filtered { f ->
                f.selector == cancelWithdrawal(address,uint).selector 
                || f.selector == completeWithdrawal(bytes32,address,uint256).selector }
{
    bytes32 contID;
    uint id1; uint id2;
    address provider1; address provider2;
    address poolToken1; address poolToken2;  
    address reserveToken1; address reserveToken2;
    uint32 createdAt1; uint32 createdAt2; 
    uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount1; uint256 reserveTokenAmount2;

    require id1 != id2;

    provider1, poolToken1, reserveToken1, createdAt1, poolTokenAmount1, 
            reserveTokenAmount1 = currentContract.withdrawalRequest(id1);
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
            reserveTokenAmount2 = currentContract.withdrawalRequest(id2);


    bothHelper(e, f, provider1, contID, id1);

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


// After successfully cancelling a withdrawal, the provider should get
// his/hers pool tokens back.
// Current status: PASSES
rule providerGetsPTsBack(uint id)
{
    env e;
    address provider = requestProvider(id);
    uint amount = requestPoolTokensAmount(id);

    require requestPoolToken(id) == ptA;
    require provider != ptA && provider != currentContract;

    uint PTbalance1 = ptA.balanceOf(e, provider);
    
    cancelWithdrawal(e, provider, id);
    
    uint PTbalance2 = ptA.balanceOf(e, provider);

    assert PTbalance1 + amount == PTbalance2;
}


