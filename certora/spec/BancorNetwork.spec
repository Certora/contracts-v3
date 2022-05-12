import "../helpers/erc20.spec"

using DummyPoolColA as PoolColA
using DummyPoolColB as PoolColB
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using DummyPoolTokenA as ptA
using DummyPoolTokenB as ptB
using DummyPoolTokenBNT as ptBNT
using MasterVault as masVault
using DummyERC20bnt as bnt
using DummyERC20vbnt as vbnt
using PendingWithdrawalsHarness as PendWit

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    // BancorNetwork
    _poolCollection(address) returns (address) envfree
    depositForPermitted(address,address,uint256,uint256,uint8,bytes32,bytes32)
    returns (uint256) envfree

    // Pool collection
    depositFor(bytes32,address,address,uint256) returns (uint256) => DISPATCHER(true)
    tradeByTargetAmount(bytes32,address,address,uint256,uint256)
                returns (uint256,uint256,uint256) => DISPATCHER(true)
    tradeBySourceAmount(bytes32,address,address,uint256,uint256)
                returns (uint256,uint256,uint256) => DISPATCHER(true)
    poolType() returns (uint16) => DISPATCHER(true)
    poolCount() returns (uint256) => DISPATCHER(true)
    poolToken(address) returns (address) => DISPATCHER(true)
    createPool(address) => DISPATCHER(true)
    withdraw(bytes32,address,address,uint256) returns (uint256) => DISPATCHER(true)
    renounceFunding(bytes32, address, uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    poolTokenToUnderlying(address, uint256) returns (uint256) => NONDET
    underlyingToPoolToken(address, uint256) returns (uint256) => NONDET

    // BNT pool
    withdraw(bytes32,address,uint256) returns (uint256) => DISPATCHER(true)
    poolTokenToUnderlying(uint256) returns (uint256) => NONDET
    underlyingToPoolToken(uint256) returns (uint256) => NONDET

    // PendingWithdrawals
    lockDuration() returns(uint32) => DISPATCHER(true)

    // Others
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)
    withdrawFunds(address, address, uint256) => DISPATCHER(true) 
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    issue(address, uint256) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    returnToken(address) returns (address) => DISPATCHER(true)
    reserveToken() returns (address) => DISPATCHER(true)
}

////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////

// TODO: add ghosts as necessary

////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////

// TODO: Add invariants; document them in reports/ExampleReport.md

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

rule reachability(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

rule checkInitWithdraw(uint amount, address poolToken)
{
    env e;
    address token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            token == returnToken(e,poolToken) &&
            tokenInPoolCollectionA(token));

    require poolToken != ptBNT;

    initWithdrawal(e,poolToken,amount);
    assert false;
}

rule noDoubleCancelling(uint amount, address poolToken)
{
    env e;
    address token = PendWit.returnToken(e,poolToken);

    require poolToken == ptBNT <=> bnt == token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            tokenInPoolCollectionA(token));
    
    uint id = initWithdrawal(e,poolToken,amount);
    cancelWithdrawal(e,id);
    cancelWithdrawal@withrevert(e,id);
    assert lastReverted;
    assert false;
}


rule checkWithdraw()
{
    env e;
    uint amount = 5;
    address token = tokenA;
    uint id = initWithdrawal(e, ptA, amount);
    require ptA == PoolColA.poolToken(e,token);
    require tokenInPoolCollectionA(token);
    require PendWit.lockDuration(e) == 0;
    withdraw(e,id);
    assert false;
}

rule tradeBalancesChanged(uint amount)
{
    env e;
    uint256 maxSourceAmount = max_uint;
    address beneficiary = e.msg.sender;
    uint256 deadline = 0;
    require e.msg.sender != masVault;
    tokensPoolCollectionsSetup(tokenA,tokenB);

    uint256 balanceA1 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB1 = tokenB.balanceOf(e,e.msg.sender);

    tradeByTargetAmount(e,tokenA,tokenB,
        amount,maxSourceAmount,deadline,beneficiary);

    uint256 balanceA2 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB2 = tokenB.balanceOf(e,e.msg.sender);
    
    //assert balanceA2 < balanceA1;
    assert balanceB1 + amount == balanceB2;
}

////////////////////////////////////////////////////////////////////////////
//                       Helper Functions                                 //
////////////////////////////////////////////////////////////////////////////
function myXor(bool A, bool B) returns bool
{
    return (!A && B) || (!B && A);
}

function tokenInPoolCollectionA(address tkn) returns bool
{
    return _poolCollection(tkn) == PoolColA;
}

function tokenInPoolCollectionB(address tkn) returns bool
{
    return _poolCollection(tkn) == PoolColB;
}
// For any two different tokens, we require them to either be in the same
// pool collection or different ones. Note that any two pool collections cannot
// share the same token.
function tokensPoolCollectionsSetup(address tknA, address tknB)
{
    require tknA != tknB;
    require myXor(tokenInPoolCollectionA(tknA), tokenInPoolCollectionB(tknA));
    require myXor(tokenInPoolCollectionA(tknB), tokenInPoolCollectionB(tknB));
}

// Token in pool collection setup
function setupTokenPoolColA(env env1, address token, address poolToken)
{
    require poolToken == ptBNT <=> token == bnt;
    require poolToken != ptBNT =>  
            token == PendWit.returnToken(env1,poolToken) &&
            tokenInPoolCollectionA(token);
}
// Token in pool collection setup
function setupTokenPoolColB(env env1, address token, address poolToken)
{
    require poolToken == ptBNT <=> token == bnt;
    require poolToken != ptBNT => 
            token == PendWit.returnToken(env1,poolToken) &&
            tokenInPoolCollectionB(token);
}