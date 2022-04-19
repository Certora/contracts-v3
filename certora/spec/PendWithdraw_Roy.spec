import "../helpers/erc20.spec"

using BancorNetwork as BN
using PoolCollection as PC
using DummyERC20B as DERC
using ERC20 as erc20
using PendingWithdrawalsHarness as MAIN

methods {
    isPoolValid(address) returns(bool) => DISPATCHER(true)
    collectionByPool(address) returns(address) => DISPATCHER(true)
    nextWithdrawalRequestId() returns(uint256) envfree
    
    reserveToken() returns(address) envfree => DISPATCHER(true)
    withdrawalRequestCount(address) envfree
    // BNT Pool
    poolTokenToUnderlying(uint256) returns(uint256) => DISPATCHER(true)
    // Pool collection
    poolTokenToUnderlying(address, uint256) returns(uint256) => DISPATCHER(true)
    //
    _bntPool() returns(address) envfree
    completeWithdrawal(bytes32,address,uint256)
    initWithdrawal(address,address,uint256) 
    returnToken(address) returns(address) envfree
    poolValidity(address) returns(bool) envfree
    burn(uint256) => DISPATCHER(true)
    //mulDivF(uint256 x,uint256 y,uint256 z) returns (uint256) envfree => MulDivSum(x,y,z)
}

// A preconditioner for a valid request.
// @note : Probably requires additions (valid pool token address),
// requiring different than zero address might be superfluous.
function ValidRequest(address provider, address poolToken,
    address reserveToken, uint32 createdAt, uint256 poolTokenAmount, 
    uint256 reserveTokenAmount)
   {
       // Maybe
       require (
            provider != 0 && poolToken != 0 && reserveToken != 0 &&
            provider != poolToken && 
            provider != reserveToken && 
            poolToken != reserveToken);
   }
// Summarization for mulDivF (currently not in use)
function MulDivSum(uint256 x,uint256 y,uint256 z) returns uint256 {
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
// monotonically increasing with amount1
rule poolTokenToUnderlyingMono(uint256 amount1,uint256 amount2){
    env e;
    require amount2 > amount1 && amount1 >0;
    uint Under1 = poolTokenToUnderlying(e,amount1);
    uint Under2 = poolTokenToUnderlying(e,amount2);
    assert Under1 < Under2;
}
// Given a previous withdrawal request with id (id),
// no further call to InitWithdrawal can override the previous withdrawal.
// In other words, any new withdrawal request must have an ID different than (id).
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

    assert (!WithdrawRevert => 
        (provider == providerInit &&
        poolTokenAmount == poolTokenAmountInit &&
        poolToken == poolTokenInit)
        ,"initWithdrawal did not register request as expected");
    
}
// Withdrawal request cannot be completed more than once.
rule NoDoubleWithdrawal(bytes32 contID, address provider, uint256 id)
{
    env e;
    completeWithdrawal(e,contID,provider,id);
    completeWithdrawal@withrevert(e,contID,provider,id);
    assert lastReverted;
}
// initWithdrawal must increase nextWithdrawalRequestId by one.
// If reverts, for any reason, the next ID musn't change.
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
// his/hers request count must increase by one
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
// his/hers request count must decrease by one
rule WithdrawalCountConsistent_Cancel(address provider, uint id)
{
    env e;
    uint ReqCountBefore = withdrawalRequestCount(provider); 
    //require ReqCountBefore > 0; // Checking for underflow is not necessary in this case.
    cancelWithdrawal(e,provider,id);
    uint ReqCountAfter = withdrawalRequestCount(provider);
    assert ReqCountAfter == ReqCountBefore-1;
}
// SANITY
rule sanity(method f)
{   
    env e;
    calldataarg args;
    f(e, args);
    assert false;
}
