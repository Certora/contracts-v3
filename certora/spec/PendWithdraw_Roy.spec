import "../helpers/erc20.spec"

using BancorNetwork as BN
using BNTPool as BNTp
using PoolCollection as PC
using DummyPoolTokenA as ptA
using ERC20 as erc20
using PendingWithdrawalsHarness as MAIN

methods {
    
    nextWithdrawalRequestId() returns(uint256) envfree
    withdrawalRequestCount(address) envfree
    lockDuration() returns(uint32) envfree
    _bntPool() returns(address) envfree
    completeWithdrawal(bytes32,address,uint256)
    initWithdrawal(address,address,uint256) 
    returnToken(address) returns(address) envfree
    poolValidity(address) returns(bool) envfree
    withdrawalRequestSpecificId(address, uint) returns uint envfree
    // Bancor Network
    collectionByPool(address) returns(address) => DISPATCHER(true)
    // BNT Pool
    poolTokenToUnderlying(uint256) returns(uint256) => DISPATCHER(true)
    stakedBalance() returns(uint256) => DISPATCHER(true)
    // Pool collection
    poolTokenToUnderlying(address, uint256) returns(uint256) => DISPATCHER(true)
    isPoolValid(address) returns(bool) => DISPATCHER(true)
    // Pool token
    reserveToken() returns (address) => DISPATCHER(true)
    // ERC20 Burnable
    burn(uint256) => DISPATCHER(true)
    //mulDivF(uint256 x,uint256 y,uint256 z) returns (uint256) envfree => MulDivSummary(x,y,z)
}

// A preconditioner for a valid request.
// @note : Probably requires additions (valid pool token address),
// requiring different than zero address might be superfluous.
function ValidRequest(address provider, address poolToken,
    address reserveToken, uint32 createdAt, uint256 poolTokenAmount, 
    uint256 reserveTokenAmount)
   {
       require (
            provider != 0 && poolToken != 0 && reserveToken != 0 &&
            provider != poolToken && 
            provider != reserveToken && 
            poolToken != reserveToken);
   }
// Preconditioner for valid index of provider requests array.
function ValidInd_Request(address provider, uint ind) returns (bool)
{
    return ind < withdrawalRequestCount(provider);
}
// Summarization for mulDivF (currently not in use)
function MulDivSummary(uint256 x,uint256 y,uint256 z) returns uint256 {
  require(z >0);
  uint256 w = (x * y) / z;
  return w;
}

////////////////////////////////////
/*
    ********** RULES ***************
*/
////////////////////////////////////
// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (BNTPool impl.)
// Current status: FAILS
// MathEX.mulDivF is uninterpreted.
rule poolTokenToUnderlyingMono1(uint256 amount1,uint256 amount2){
    env e;
    require amount2 > amount1 && amount1 >0;
    require BNTp.stakedBalance(e) > 0;
    uint UAmount1 = BNTp.poolTokenToUnderlying(e,amount1);
    uint UAmount2 = BNTp.poolTokenToUnderlying(e,amount2);
    assert UAmount1 < UAmount2;
}

// Conversion from pool token to any underlying token is 
// monotonically increasing with amount (PoolCollection impl.)
// Current status: FAILS
// MathEX.mulDivF is uninterpreted.
rule poolTokenToUnderlyingMono2(uint256 amount1,uint256 amount2){
    env e;
    address pool;
    require amount2 > amount1 && amount1 >0;
    uint UAmount1 = PC.poolTokenToUnderlying(e,pool,amount1);
    uint UAmount2 = PC.poolTokenToUnderlying(e,pool,amount2);
    assert UAmount1 < UAmount2;
}

// Given a previous withdrawal request with id (id),
// no further call to InitWithdrawal can override the previous withdrawal.
// In other words, any new withdrawal request must have an ID different than (id).
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
        reserveTokenAmount = currentContract.withdrawalRequest(e,id);

    // require that request is valid.
    ValidRequest(provider,poolToken,reserveToken,createdAt,
    poolTokenAmount,reserveTokenAmount);
    require id < nextWithdrawalRequestId();
    // If initWithdrawal completed successfully, it must not override 
    // the previously defined request.
    id2 = initWithdrawal(e,provider2,poolToken2,poolTokenAmount2);
    assert id2 != id;
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

    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
        reserveTokenAmount = currentContract.withdrawalRequest(e,id);

    assert(provider == providerInit &&
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
    assert lastReverted;
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
    assert !reverted => id1+1 == id2;
    assert reverted => id1 == id2;
}

// Attempt to use struct in CVL - IGNORE
/*
rule StructWithdrawalRequest(uint id)
{
    MAIN.WithdrawalRequest var;
    address provider;
    env e;
    sinvoke cancelWithdrawal(e,provider, id);
    require var == MAIN.withdrawalRequest(e,id) ;
    assert var.provider == 0;
}*/
//
// Any cancelled request with a given id, must not be associated
// to any provider (including the original).
// Current status: PASSES
rule CancelWithdrawalIntegrity(uint id, address pro)
{
    env e;
    //
    address provider1; address provider2;
    address poolToken1; address poolToken2;  
    address reserveToken1; address reserveToken2;
    uint32 createdAt1; uint32 createdAt2; 
    uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 reserveTokenAmount1; uint256 reserveTokenAmount2;
    provider1, poolToken1, reserveToken1, createdAt1, poolTokenAmount1, 
    reserveTokenAmount1 = currentContract.withdrawalRequest(e,id);
    //
    require provider1 == pro;
    cancelWithdrawal(e,provider1, id);
    //
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
    reserveTokenAmount2 = currentContract.withdrawalRequest(e,id);
    assert provider2 == 0;
    //
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
    require ReqCountBefore < max_uint ; // Neglecting overflow case
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
    //require ReqCountBefore > 0; // Checking for underflow is not necessary in this case.
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
    require poolToken == ptA;
    uint256 Amount;
    uint id;
    id = initWithdrawal(e,provider,poolToken,Amount);
    // This probably holds all the time. See lockDurationNotZero.
    // In the future, we can replace this by an invariant requirement.
    require lockDuration() > 0; 
    assert !isReadyForWithdrawal(e,id); 
    completeWithdrawal@withrevert(e,contID,provider,id);
    assert lastReverted;
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
    restriction on the value. 
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
// Current status: FAILS.
// cancelWithdrawal reverts because safeTransfer call in _cancelWithdrawal reverts.
// One has to make sure that the protocol has enough pool tokens in balance.
// This could be assumed if we are sure that they were given to the protocol in advance.
rule CancellingAlwaysPossible(address provider)
{
    env e;
    address poolToken;
    require poolToken == ptA;
    uint256 Amount;
    uint id;
    id = initWithdrawal(e,provider,poolToken,Amount);
    // No restriction upon the request count can lead to overflow,
    // thus "remove" function can return false.
    // Here the limit is arbitrary.
    require withdrawalRequestCount(provider) < 100000;
    cancelWithdrawal@withrevert(e,provider,id);
    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}

// Only provider can ask to withdraw request.
// Current status: PASSES
rule WithdrawByProviderOnly(address provider)
{
    env e;
    address poolToken; bytes32 contID;
    require poolToken == ptA;
    uint256 Amount; address provider2;
    uint id;
    id = initWithdrawal(e,provider,poolToken,Amount);
    completeWithdrawal(e,contID,provider2,id);
    assert provider2 == provider;
}

// Only provider can ask to cancel request.
// Current status: PASSES
rule CancelByProviderOnly(address provider)
{
    env e;
    address poolToken;
    require poolToken == ptA;
    uint256 Amount; address provider2;
    uint id;
    id = initWithdrawal(e,provider,poolToken,Amount);
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
    require Count1 < 100;
    // Now, adding a request to the end of the list.
    // List should be now Count1+1 items long.
    uint id1 = initWithdrawal(e,provider,poolToken,Amount);
    // Thus, the index Count1+2 must be out of bounds.
    withdrawalRequestSpecificId@withrevert(provider,Count1+2);
    assert lastReverted;
    // Adding another one.
    uint id2 = initWithdrawal(e,provider,poolToken,Amount);
    // In total, we added two subsequent requests. Validating that
    // function gets them properly.
    assert id1 == withdrawalRequestSpecificId(provider,Count1+1);
    assert id2 == withdrawalRequestSpecificId(provider,Count1+2);
}
/*
// No two identical Ids for provider
// WORK IN PROGRESS
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
    uint count = withdrawalRequestCount(provider);
    require ind1 <= count && ind2 <= count;
    uint id1 = withdrawalRequestSpecificId(provider,ind1);
    uint id2 = withdrawalRequestSpecificId(provider,ind2);
}
*/
// Reachability
// Current status: FAILS for all functions.
rule reachability(method f)
{   
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}
