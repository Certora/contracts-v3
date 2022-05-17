import "../helpers/erc20.spec"

using PoolCollectionHarness as PoolCol
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using DummyPoolTokenA as ptA
using DummyPoolTokenB as ptB
using DummyPoolTokenBNT as ptBNT
using BNTPool as BNTp
using MasterVault as masVault
using ExternalProtectionVault as EPV
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
    createPool(address) => DISPATCHER(true)
    withdraw(bytes32,address,address,uint256) returns (uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    PoolCol.poolTokenToUnderlying(address, uint256) returns (uint256) envfree
    PoolCol.underlyingToPoolToken(address, uint256) returns (uint256) envfree
    PoolCol.getPoolDataBntTradingLiquidity(address) returns(uint128) envfree
    PoolCol.poolToken(address) returns (address) envfree
    PoolCol.defaultTradingFeePPM() returns (uint32) envfree
    PoolCol.tokenUserBalance(address, address) returns (uint256) envfree

    // BNT pool
    BNTp.withdraw(bytes32,address,uint256) returns (uint256) 
    BNTp.poolTokenToUnderlying(uint256) returns (uint256)
    BNTp.underlyingToPoolToken(uint256) returns (uint256) 
    BNTp.availableFunding(address) returns (uint256)
    BNTp.requestFunding(bytes32,address,uint256)
    BNTp.renounceFunding(bytes32,address,uint256)

    // PendingWithdrawals
    PendWit.lockDuration() returns(uint32) envfree
    PendWit.completeWithdrawal(bytes32,address,uint256) returns ((address,uint256))
    PendWit.returnToken(address) returns (address) envfree 

    // Others
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)
    EPV.withdrawFunds(address, address, uint256)
    masVault.withdrawFunds(address, address, uint256)
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    issue(address, uint256) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    reserveToken() returns (address) => DISPATCHER(true)
    mulDivF(uint256 x,uint256 y,uint256 z) returns (uint256) => simpleMulDiv(x,y,z)
    mulDivC(uint256 x,uint256 y,uint256 z) returns (uint256) => simpleMulDiv(x,y,z)
}

////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////


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

rule underlyingToPTinverse(uint amount)
{
    address token = tokenA;
    address poolTok = ptA;

    require PoolCol.poolToken(token) == poolTok;

    uint a = PoolCol.poolTokenToUnderlying(token,amount);
    uint b = PoolCol.underlyingToPoolToken(token,a);
    
    assert b == amount;
}

rule checkDepositFor(address provider, uint256 amount)
{
    env e;
    uint256 a = depositFor(e,provider,bnt,amount);
    assert false;
}

rule checkWithdrawFees(address beneficiary)
{
    env e;
    uint256 Fee = pendingNetworkFeeAmount(e);
    withdrawNetworkFees(e,beneficiary);
    assert false;
}

rule checkInitWithdraw(uint amount, address poolToken)
{
    env e;
    address token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            token == PendWit.returnToken(poolToken) &&
            tokenInPoolCollection(token,PoolCol));

    require poolToken != ptBNT;

    initWithdrawal(e,poolToken,amount);
    assert false;
}

rule noDoubleCancelling(uint amount, address poolToken)
{
    env e;
    address token = PendWit.returnToken(poolToken);

    require poolToken == ptBNT <=> bnt == token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            tokenInPoolCollection(token,PoolCol));
    
    uint id = initWithdrawal(e,poolToken,amount);
    cancelWithdrawal(e,id);
    cancelWithdrawal@withrevert(e,id);
    assert lastReverted;
}

rule checkWithdraw()
{
    env e;
    uint amount;
    address token = tokenA;
    address poolToken = ptA;

    require PendWit.lockDuration() == 0;
    setupTokenPoolCol(e,token,poolToken);
    uint id = initWithdrawal(e,poolToken,amount);
        withdraw(e,id);
    assert false;
}


rule tradeBntLiquidity(uint amount)
{
    env e;
    uint256 maxSourceAmount = max_uint;
    uint256 deadline = 0;
    address beneficiary = e.msg.sender;
    address tknA = tokenA;
    address tknB = tokenB;
    address poolTokenA = ptA;
    address poolTokenB = ptB;
    require PoolCol.defaultTradingFeePPM() <= 10000;

    require e.msg.sender != masVault;
    // Assuming both tokens are in the same poolCollection
    require poolTokenA == PoolCol.poolToken(tokenA) &&
            _poolCollection(tknA) == PoolCol;

    require poolTokenB == PoolCol.poolToken(tokenB) &&
            _poolCollection(tknB) == PoolCol;

    uint128 bntLiqA1 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB1 = PoolCol.getPoolDataBntTradingLiquidity(tknB);

    tradeByTargetAmount(e,tknA,tknB,
        amount,maxSourceAmount,deadline,beneficiary);

    uint128 bntLiqA2 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB2 = PoolCol.getPoolDataBntTradingLiquidity(tknB);
    //assert false;
    assert bntLiqA2 <= bntLiqA1 && bntLiqB1 <= bntLiqB2;
}


// Verified
rule RequestRegisteredForValidProvider(uint tokenAmount)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;
    address provider = e.msg.sender;
    require provider != PendWit;
    setupTokenPoolCol(e,token,poolToken);

    uint balance1 = ptA.balanceOf(e,provider);
        uint id = initWithdrawal(e,poolToken,tokenAmount);
    uint balance2 = ptA.balanceOf(e,provider);

    assert balance1 - balance2 == tokenAmount &&
            balance1 >= tokenAmount;
}

rule whoChangedMasterVaultBalance(method f)
filtered{f->f.selector!=withdraw(uint).selector}
{
    env e;
    calldataarg args;
    uint balanceTKN1 = tokenA.balanceOf(e,masVault);
    uint balanceBNT1 = bnt.balanceOf(e,masVault);
    f(e,args);
    uint balanceTKN2 = tokenA.balanceOf(e,masVault);
    uint balanceBNT2 = bnt.balanceOf(e,masVault);
    assert balanceBNT2 == balanceBNT1 &&
            balanceTKN1 == balanceTKN2;
}

rule noDoubleWithdrawal(uint256 ptAmount)
{
    env e;
    address poolToken;
    address token;
    require poolToken == ptA || poolToken == ptBNT;
    setupTokenPoolCol(e,token,poolToken);
    
    uint id;// = initWithdrawal(e,poolToken,ptAmount);
    uint256 withAmount = withdraw(e,id);
    withdraw@withrevert(e,id);
    
    assert lastReverted;
}

rule depositBNT(uint256 amount)
{
    env e;
    require e.msg.sender != currentContract &&
            e.msg.sender != PendWit;

    uint balance1 = ptBNT.balanceOf(e,e.msg.sender);
    uint balanceBNT1 = bnt.balanceOf(e,e.msg.sender);

    uint amountPT = deposit(e,bnt,amount);
    //uint id = initWithdrawal(e,poolToken, amountPT);

    uint balance2 = ptBNT.balanceOf(e,e.msg.sender);
    uint balanceBNT2 = bnt.balanceOf(e,e.msg.sender);

    assert false;
    assert balance2 == balance1 + amountPT , "User's PT balance did not increase as expected";
    //assert balanceBNT1 == balanceBNT2 + amount , "User's BNT balance did not decrease as expected";
}

////////////////////////////////////////////////////////////////////////////
//                       Helper Functions                                 //
////////////////////////////////////////////////////////////////////////////
function validUser(env env1, address user) returns bool
{
    return user != currentContract &&
            user != _masterVault(env1) &&
            user != _externalProtectionVault(env1) &&
            user != _pendingWithdrawals(env1) &&
            user != _bntPool(env1);
}

function myXor(bool A, bool B) returns bool
{
    return (!A && B) || (!B && A);
}

function tokenInPoolCollection(address tkn, address PoolCollect) returns bool
{
    return _poolCollection(tkn) == PoolCollect;
}

// For any two different tokens, we require them to either be in the same
// pool collection or different ones. Note that any two pool collections cannot
// share the same token.
function tokensPoolCollectionsSetup(address tknA, address tknB, address PoolColA, address PoolColB)
{
    require tknA != tknB;
    require PoolColA != PoolColB;
    require myXor(tokenInPoolCollection(tknA, PoolColA), tokenInPoolCollection(tknA, PoolColB));
    require myXor(tokenInPoolCollection(tknB, PoolColA), tokenInPoolCollection(tknB, PoolColB));
}

// Token in pool collection setup
function setupTokenPoolCol(env env1, address token, address PT)
{
    require PT == ptBNT <=> token == bnt;
    require PT != ptBNT =>  
            PT == PoolCol.poolToken(token) &&
            tokenInPoolCollection(token,PoolCol);
}

function constQuotientMulDiv(uint256 x, uint256 y, uint256 z, uint256 q)
returns uint256
{
    uint256 f;
    require z != 0;
    require ( x==q*z && f==q*y ) || ( y==q*z && f==q*x ) || 
            ( q*x==z && f==y/q && y%q ==0 ) || ( q*y==z && f==x/q && x%q ==0);
    return f;
}

function simpleMulDiv(uint256 x,uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    // We restrict to no remainders
    // Possible quotients : Qut[q] means that y/z or x/z is q.
    bool Qut0 = (x==0 || y==0) && (f == 0);
    bool Qut1 = ( x==z && f==y ) || ( y==z && f==x );
    bool Qut2 = ( x==2*z && f==2*y ) || ( y==2*z && f==2*x );
    bool Qut3 = ( x==3*z && f==3*y ) || ( y==3*z && f==3*x );
    bool Qut10 = ( x==10*z && f==10*y ) || ( y==10*z && f==10*x );
    bool Qut1_2 = ( 2*x==z && f==y/2 && y%2 ==0) || ( 2*y==z && f==x/2 && x%2 ==0);
    bool Qut1_3 = ( 3*x==z && f==y/3 && y%3 ==0 ) || ( 3*y==z && f==x/3 && x%3 ==0);
    bool Qut1_10 = ( 10*x==z && f==y/10 && y%10 ==0 ) || 
                    ( 10*y==z && f==x/10 && x%10 ==0);

    require dontDividebyZero;
    require Qut0 || Qut1 || Qut2 || Qut3 || Qut10 || Qut1_2 || Qut1_3 || Qut1_10;
    return f;
}


function simpleMulDivIf(uint256 x,uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    bool Success = true;
    require dontDividebyZero;

    if(x == 0 || y==0)    {f = 0;}
    else if(y == 2 * z)     {f=2*x;}
    else if(y == 3 * z)     {f=3*x;}
    else if(y == 10 * z)    {f=10*x;}
    else if(2*y==z && x%2 ==0)  {f=x/2;}
    else if(3*y==z && x%3 ==0)  {f=x/3;}
    else if(10*y==z && x%10 ==0)    {f=x/10;}
    else if(y==z)   { f=x; }
    else    {f = 0; Success = false;}

    require Success;
    return f;
}


function mulDivFactor2(uint256 x,uint256 y, uint256 z) returns uint256 
{
    require z!=0;
    if(x==0 || y==0){
        return 0;
    }
    else if(y>z){
        return to_uint256(2*x);
    }
    else if(y<z){
        return to_uint256(x/2);
    }
    else{
        return x;
    }
}

function identity(uint256 x) returns uint256 
{
    return x;
}
