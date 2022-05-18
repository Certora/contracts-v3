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
    collectionByPool(address) returns (address) envfree
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
    poolTokenToUnderlying(address, uint256) returns (uint256) => DISPATCHER(true)
    underlyingToPoolToken(address, uint256) returns (uint256) => DISPATCHER(true)
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
    PendWit._network() returns (address)
    PendWit.lockDuration() returns(uint32) envfree
    PendWit.completeWithdrawal(bytes32,address,uint256) returns ((address,uint256))
    PendWit.returnToken(address) returns (address) envfree
    PendWit.withdrawalRequest(uint256) returns 
            ((address, address, address, uint32,uint256,uint256)) envfree 

    // Others
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)
    EPV.withdrawFunds(address, address, uint256)
    masVault.withdrawFunds(address, address, uint256)
    isTokenWhitelisted(address) returns (bool) => DISPATCHER(true)
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
    mulDivF(uint256 x,uint256 y,uint256 z) returns (uint256) => simpleMulDivIf(x,y,z)
    mulDivC(uint256 x,uint256 y,uint256 z) returns (uint256) => simpleMulDivIf(x,y,z)
}

////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////

//https://vaas-stg.certora.com/output/41958/dcdc01d1ce1740249872/?anonymousKey=42f1ef1a1e0a739ed3b34b06109fae02ffb6abcb
invariant poolLinkPoolCollection(address pool)
    collectionByPool(pool) == PoolCol <=> _poolCollection(pool) == PoolCol

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
    env e;
    address token = tokenA;
    address poolTok = ptA;

    require PoolCol.poolToken(token) == poolTok;

    uint a = poolTokenToUnderlying(e,token,amount);
    uint b = underlyingToPoolToken(e,token,a);
    
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

// Verified
rule checkInitWithdraw(uint amount, address poolToken)
{
    env e;
    address token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            token == ptA.reserveToken(e) &&
            tokenInPoolCollection(token,PoolCol));

    require poolToken == ptBNT =>
            (token == bnt && token == ptBNT.reserveToken(e));

    uint id = initWithdrawal(e,poolToken,amount);

    address provider;
    address poolToken2;
    address reserveToken;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;

    provider, poolToken2, reserveToken, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);
    assert poolToken2 == poolToken, "Pool token not registered correctly";
    assert reserveToken == token, "Reserve token not registered correctly";
    assert provider == e.msg.sender, "Provider is not the original message sender";
    assert poolTokenAmount == amount, "Pool token amount was not registered correctly";
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
    uint256 balanceA1 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB1 = tokenB.balanceOf(e,e.msg.sender);

    tradeByTargetAmount(e,tknA,tknB,
        amount,maxSourceAmount,deadline,beneficiary);

    uint128 bntLiqA2 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB2 = PoolCol.getPoolDataBntTradingLiquidity(tknB);
    uint256 balanceA2 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB2 = tokenB.balanceOf(e,e.msg.sender);

    //assert false;
    assert bntLiqA2 <= bntLiqA1 && bntLiqB1 <= bntLiqB2;
    assert balanceA1 >= balanceA2;
    assert balanceB1 + amount == balanceB2;
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

rule noDoubleWithdrawalBNT(uint256 ptAmount)
{
    env e;
    address poolToken;
    address token = bnt;
    require poolToken == ptBNT;
    require ptBNT.reserveToken(e) == token;
    
    uint id = initWithdrawal(e,poolToken,ptAmount);
    uint256 withAmount = withdraw(e,id);
    withdraw@withrevert(e,id);
    
    assert lastReverted;
}

// Is reachable.
rule noDoubleWithdrawalTKN(uint256 ptAmount, uint id)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;
    require ptA.reserveToken(e) == token;
    setupTokenPoolCol(e,token,poolToken);
    require collectionByPool(token) == PoolCol;

    // Set withdrawal request id
    address provider;
    address poolToken2;
    address reserveToken;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;
    provider, poolToken2, reserveToken, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);
    // Require consistency
    require provider == e.msg.sender;
    require poolToken2 == poolToken;
    require ptAmount == poolTokenAmount;

    // Withdraw:
    uint256 withAmount = withdraw(e,id);
    withdraw@withrevert(e,id);
    assert lastReverted;
}

rule depositBntIntegrity(uint256 amount)
{
    env e;
    require validUser(e,e.msg.sender);
    require ptBNT.reserveToken(e) == bnt;

    // Balances before deposit
    uint balancePT1 = ptBNT.balanceOf(e,e.msg.sender);
    uint balanceBNT1 = bnt.balanceOf(e,e.msg.sender);
    // Deposit (amount) BNT to pool.
    uint amountPT = deposit(e,bnt,amount);
    // Balances after deposit, before withdrawal.
    uint balancePT2 = ptBNT.balanceOf(e,e.msg.sender);
    uint balanceBNT2 = bnt.balanceOf(e,e.msg.sender);

    assert balanceBNT2 == balanceBNT1 - amount, 
            "User's BNT balance did not decrease as expected";
    assert balancePT2 == balancePT1 + amountPT, 
            "User's PT balance did not increase as expected";

    // Request to withdraw.
    uint id = initWithdrawal(e,ptBNT, amountPT);
    // Balances after withdraw request.
    uint balancePT3 = ptBNT.balanceOf(e,e.msg.sender);
    uint balanceBNT3 = bnt.balanceOf(e,e.msg.sender);

    assert balancePT3 == balancePT1 , "User's PT balance changed unexpectedly";
}
// Verified
//https://vaas-stg.certora.com/output/41958/5e2069df2a8c46f91103/?anonymousKey=2116b7dac8dbe7a77a68c082c2260df6bff713d8
rule depositTknIntegrity(uint256 amount)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;

    require validUser(e,e.msg.sender);
    require ptA.reserveToken(e) == token;
    setupTokenPoolCol(e,token,poolToken);
    require collectionByPool(token) == PoolCol;

    // Balances before deposit
    uint balancePT1 = ptA.balanceOf(e,e.msg.sender);
    uint balanceTKN1 = tokenA.balanceOf(e,e.msg.sender);
    // Deposit (amount) BNT to pool.
    uint amountPT = deposit(e,token,amount);
    // Balances after deposit, before withdrawal.
    uint balancePT2 = ptA.balanceOf(e,e.msg.sender);
    uint balanceTKN2 = tokenA.balanceOf(e,e.msg.sender);
    
    assert balanceTKN2 == balanceTKN1 - amount, 
            "User's BNT balance did not decrease as expected";
    assert balancePT2 == balancePT1 + amountPT, 
            "User's PT balance did not increase as expected";

    // Request to withdraw.
    uint id = initWithdrawal(e,poolToken,amountPT);
    // Balances after withdraw request.
    uint balancePT3 = ptA.balanceOf(e,e.msg.sender);
    uint balanceTKN3 = tokenA.balanceOf(e,e.msg.sender);

    assert balancePT3 == balancePT1 , "User's PT balance changed unexpectedly";
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
    require ( x == q * z && f==q * y ) || 
            ( q * x == z && f == y / q && y % q ==0 ) ||
            ( y == 2 * z && f == 2 * x ) || 
            ( 2 * y == z && f == x / 2 && x % 2 ==0);
    return f;
}

function simpleMulDiv(uint256 x,uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    // We restrict to no remainders
    // Possible quotients : Qut[q] means that y/z or x/z is q.
    bool Qut0 = (x ==0 || y ==0) && (f == 0);
    bool Qut1 = ( x == z && f == y ) || ( y == z && f == x );
    bool Qut2 = ( x == 2 * z && f == 2 * y ) || ( y == 2 * z && f == 2 * x );
    bool Qut3 = ( x == 3 * z && f == 3 * y ) || ( y == 3 * z && f == 3 * x );
    bool Qut10 = ( x == 10 * z && f==10*y ) || ( y== 10 * z && f == 10 * x );
    bool Qut1_2 = ( 2 * x == z && f == y / 2 && y % 2 ==0) || ( 2 * y ==z && f == x/2 && x % 2 ==0);
    bool Qut1_3 = ( 3 * x == z && f == y / 3 && y % 3 ==0) || ( 3 * y ==z && f == x/3 && x % 3 ==0);
    bool Qut1_10 = ( 10 * x == z && f == y / 10 && y % 10 ==0) || 
                    ( 10 * y == z && f == x/ 10 && x % 10 ==0);

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

    if(x ==0 || y ==0)      {f = 0;}
    else if(y == 2 * z)     {f = 2 * x;}
    else if(y == 3 * z)     {f = 3 * x;}
    else if(y == 10 * z)    {f = 10 * x;}
    else if(2 * y == z && x % 2 ==0)  {f = x / 2;}
    else if(3 * y == z && x % 3 ==0)  {f = x / 3;}
    else if(10*y == z && x % 10 ==0)    {f = x / 10;}
    else if(y == z)   { f = x;}
    else    {f = 0; Success = false;}

    require Success;
    return f;
}


function mulDivFactor2(uint256 x,uint256 y, uint256 z) returns uint256 
{
    require z !=0;
    if(x == 0 || y == 0){
        return 0;
    }
    else if(y > z){
        return to_uint256(2 * x);
    }
    else if(y < z){
        return to_uint256(x / 2);
    }
    else{
        return x;
    }
}

function identity(uint256 x) returns uint256 
{
    return x;
}
