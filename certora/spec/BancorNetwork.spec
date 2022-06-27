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
using DummyTokenGovernanceA as BntGovern
using DummyTokenGovernanceB as VbntGovern
using DummyERC20vbnt as vbnt
using PendingWithdrawalsHarness as PendWit
using NetworkSettings as networkSettings

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    // BancorNetwork
    _poolCollection(address) returns (address) envfree
    collectionByPool(address) returns (address) envfree

    depositFor(address, address, uint256) returns (uint256) 
    deposit(address, uint256) returns (uint256) 

    /*
    depositForPermitted(address, address, uint256, uint256, 
            uint8, bytes32, bytes32) returns (uint256) 

    depositPermitted(address, uint256, uint256,
            uint8, bytes32, bytes32) returns (uint256) 
    */

    //_withdrawContextId(uint256, address) returns(bytes32)

    flashLoan(address, uint256, address, bytes) => DISPATCHER(true)

    // Pool collection
    depositFor(bytes32, address, address, uint256) returns (uint256) => DISPATCHER(true)
    tradeByTargetAmount(bytes32, address, address, uint256, uint256)
                returns (uint256, uint256, uint256) => DISPATCHER(true)
    tradeBySourceAmount(bytes32, address, address, uint256, uint256)
                returns (uint256, uint256, uint256) => DISPATCHER(true)
    poolType() returns (uint16) => DISPATCHER(true)
    poolCount() returns (uint256) => DISPATCHER(true)
    createPool(address) => DISPATCHER(true)
    poolToken(address) returns (address) => DISPATCHER(true)
    withdraw(bytes32, address, address, uint256, uint256) returns (uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    poolTokenToUnderlying(address, uint256) returns (uint256) => DISPATCHER(true)
    underlyingToPoolToken(address, uint256) returns (uint256) => DISPATCHER(true)
    onFeesCollected(address, uint256) => DISPATCHER(true)
    flashLoanFeePPM() returns (uint32) => DISPATCHER(true)
    PoolCol.getPoolDataTradingFee(address) returns (uint32) envfree
    PoolCol.getPoolDataStakedBalance(address) returns (uint256) envfree
    PoolCol.getPoolDataBntTradingLiquidity(address) returns(uint128) envfree
    PoolCol.getPoolDataBaseTokenLiquidity(address) returns(uint128) envfree
    PoolCol.poolToken(address) returns (address) envfree
    PoolCol.defaultTradingFeePPM() returns (uint32) envfree
    PoolCol.tokenUserBalance(address, address) returns (uint256) envfree
    PoolCol.isPoolValid(address) returns(bool) envfree
    migratePoolOut(address, address) => DISPATCHER(true)
    migratePoolIn(address, address) => DISPATCHER(true)

    createPoolToken(address) returns(address) => DISPATCHER(true)
    acceptOwnership() => DISPATCHER(true)

    // BNT pool
    BNTp.withdraw(bytes32, address, uint256, uint256) returns (uint256) 
    BNTp.poolTokenToUnderlying(uint256) returns (uint256)
    BNTp.underlyingToPoolToken(uint256) returns (uint256) 
    BNTp.availableFunding(address) returns (uint256)
    BNTp.requestFunding(bytes32, address, uint256)
    BNTp.renounceFunding(bytes32, address, uint256)

    // PendingWithdrawals
    PendWit.poolTotalSupply(address) returns (uint256) envfree
    PendWit._network() returns (address)
    PendWit.lockDuration() returns(uint32) envfree
    PendWit.completeWithdrawal(bytes32, address, uint256) returns ((address, uint256, uint256))
    PendWit.returnToken(address) returns (address) envfree
    PendWit.withdrawalRequest(uint256) returns 
            ((address, address, address, uint32, uint256, uint256)) envfree 

    // Governance
    BntGovern._token() returns(address) envfree
    VbntGovern._token() returns(address) envfree

    // Others
    onFlashLoan(address, address, uint256, uint256, bytes) => DISPATCHER(true)
    permit(address, address, uint256, uint256, uint8, bytes32, bytes32) => DISPATCHER(true)
    EPV.withdrawFunds(address, address, uint256)
    masVault.withdrawFunds(address, address, uint256)
    isTokenWhitelisted(address) returns (bool) => DISPATCHER(true)
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    issue(address, uint256) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    sendTo() returns(bool) => DISPATCHER(true)
    sendValue() returns(bool) => DISPATCHER(true)
    reserveToken() returns (address) => DISPATCHER(true)
    mulDivF(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDivIfWithRemainder(x,y,z)
    mulDivC(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDivIfWithRemainder(x,y,z)
    hasRole(bytes32, address) returns(bool) envfree
    roleAdmin() returns(bytes32) envfree
    roleMigrationManager() returns(bytes32) envfree
    roleEmergencyStopper() returns(bytes32) envfree
    roleNetworkFeeManager() returns(bytes32) envfree
    isPaused() returns(bool) envfree
    ethBalance() returns(uint256) envfree

    // PoolMigrator
    migratePool(address) returns(address) => DISPATCHER(true)
}


////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////
// Total pool tokens in registerd requests
ghost sumRequestPoolTokens(address) returns uint256 {
    init_state axiom forall address PT. sumRequestPoolTokens(PT) == 0;
}

// Sum of pool tokens balances (for all users)
ghost sumPTbalances(address) returns uint256 {
    init_state axiom forall address PT. sumPTbalances(PT) == 0;
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
hook Sstore PendWit._withdrawalRequests[KEY uint256 id].poolToken address PT STORAGE {
    havoc requestPoolTokenGhost assuming forall uint256 id2.
    id2 == id => requestPoolTokenGhost@new(id2) == PT;
}

// Hook to havoc the provider of request (id)
hook Sstore PendWit._withdrawalRequests[KEY uint256 id].provider address Provider STORAGE {
    havoc requestProviderGhost assuming forall uint256 id2.
    id == id2 => requestProviderGhost@new(id2) == Provider;
}

// Hook to havoc the total number of pool tokens registered in requests.
hook Sstore PendWit._withdrawalRequests[KEY uint256 id].poolTokenAmount uint256 balance (uint256 old_balance) STORAGE {
    havoc sumRequestPoolTokens assuming forall address poolToken.
    ((requestPoolTokenGhost(id) == poolToken) ?
    sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken) + balance - old_balance :
    sumRequestPoolTokens@new(poolToken) == sumRequestPoolTokens@old(poolToken));
}


definition depositLikeMethod(method f) returns bool = 
        f.selector == depositFor(address, address, uint256).selector ||
        f.selector == deposit(address, uint256).selector;

        /*f.selector == depositForPermitted(address, address, uint256, uint256, 
            uint8, bytes32, bytes32).selector ||

        f.selector == depositPermitted(address, uint256, uint256, 
            uint8, bytes32, bytes32).selector ;
            */  

definition tradeLikeMethod(method f) returns bool = 
        f.selector == 
        tradeBySourceAmount(address, address, uint256, uint256, uint256, address)
        .selector ||
        
        f.selector == 
        tradeByTargetAmount(address, address, uint256, uint256, uint256, address)
        .selector;

        /*
        f.selector == 
        tradeBySourceAmountPermitted(address, address, uint256, uint256, uint256, address,
        uint8, bytes32, bytes32).selector ||

        f.selector == 
        tradeByTargetAmountPermitted(address, address, uint256, uint256, uint256, address,
        uint8, bytes32, bytes32).selector;
        */

// A restriction upon the value of f = x * y / z
// The division quotient y/z or x/z can be either q or 1/q.
// No division remainders are assumed.
// Important : do not set q=0.
definition constQuotient(uint256 x, uint256 y, uint256 z, uint256 q, uint256 f) 
        returns bool = 
        ( x == q * z && f == q * y ) || 
        ( q * x == z && f == y / q && y % q ==0 ) ||
        ( y == q * z && f == q * x ) || 
        ( q * y == z && f == x / q && x % q ==0);

// Allowing division remainders
definition constQuotientWithRemainder(uint256 x, uint256 y, uint256 z, uint256 q, uint256 f) 
        returns bool = 
        ( x == q * z && f == q * y ) || 
        ( q * x == z && f == y / q ) ||
        ( y == q * z && f == q * x ) || 
        ( q * y == z && f == x / q );

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
            tokenInPoolCollection(token, PoolCol);
}

// Summary for mulDivF:
// quotient y/z is either 0,1,2,3,10 or 1/2, 1/3, 1/10.
function simpleMulDivIf(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    bool Success = dontDividebyZero;
    uint256 qs = 400; // My special quotient

    if (x ==0 || y ==0)      {f = 0;}
    else if (y == z)   { f = x;}
    else if (x == z)   { f = y;}
    // Qut = 2, 1/2
    else if (y == 2 * z)     {f = 2 * x;}
    else if (x == 2 * z)     {f = 2 * y;}
    else if (2 * y == z && x % 2 == 0)  {f = x / 2;}
    else if (2 * x == z && y % 2 == 0)  {f = y / 2;}
    // Qut = 3, 1/3
    else if (y == 3 * z)     {f = 3 * x;}
    else if (x == 3 * z)     {f = 3 * y;}
    else if (3 * y == z && x % 3 == 0)  {f = x / 3;}
    else if (3 * x == z && y % 3 == 0)  {f = y / 3;}
    // Qut = 10, 1/10
    else if (y == 10 * z)     {f = 10 * x;}
    else if (x == 10 * z)     {f = 10 * y;}
    else if (10 * y == z && x % 10 == 0)  {f = x / 10;}
    else if (10 * x == z && y % 10 == 0)  {f = y / 10;}
    // Qut = 500, 1/500
    else if (y == 500 * z)     {f = 500 * x;}
    else if (x == 500 * z)     {f = 500 * y;}
    else if (500 * y == z && x % 500 == 0)  {f = x / 500;}
    else if (500 * x == z && y % 500 == 0)  {f = y / 500;}
    // Qut = qs, 1/qs
    else if (y == qs * z)     {f = qs * x;}
    else if (x == qs * z)     {f = qs * y;}
    else if (qs * y == z && x % qs == 0)  {f = x / qs;}
    else if (qs * x == z && y % qs == 0)  {f = y / qs;}
    //
    else    {f = 0; Success = false;}
    require Success;
    return f;
}

// Summary for mulDivF (with remainders)
function simpleMulDivIfWithRemainder(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    bool Success = dontDividebyZero;

    if (x ==0 || y ==0)      {f = 0;}
    else if (y == z)   { f = x;}
    else if (x == z)   { f = y;}
    // Qut = 2, 1/2
    else if (y == 2 * z)     {f = 2 * x;}
    else if (x == 2 * z)     {f = 2 * y;}
    else if (2 * y == z )  {f = x / 2;}
    else if (2 * x == z )  {f = y / 2;}
    // Qut = 3, 1/3
    else if (y == 3 * z)     {f = 3 * x;}
    else if (x == 3 * z)     {f = 3 * y;}
    else if (3 * y == z )  {f = x / 3;}
    else if (3 * x == z )  {f = y / 3;}
    // Qut = 10, 1/10
    //else if (y == 10 * z)     {f = 10 * x;}
    //else if (x == 10 * z)     {f = 10 * y;}
    //else if (10 * y == z )  {f = x / 10;}
    //else if (10 * x == z )  {f = y / 10;}
    // Qut = 500, 1/500
    else if (y == 500 * z)     {f = 500 * x;}
    else if (x == 500 * z)     {f = 500 * y;}
    else if (500 * y == z )  {f = x / 500;}
    else if (500 * x == z )  {f = y / 500;}
    //
    else    {f = 0; Success = false;}

    require Success;
    return f;
}

// Summary for mulDivF:
// A function which assumes a constant quotient y/z or x/z q (or 1/q).
function constQuotientMulDiv(uint256 x, uint256 y, uint256 z, uint256 qs)
returns uint256
{
    uint256 f;
    bool Success =  z != 0;
    // Qut = qs, 1/qs
    if (y == qs * z)     {f = qs * x;}
    else if (x == qs * z)     {f = qs * y;}
    else if (qs * y == z && x % qs == 0)  {f = x / qs;}
    else if (qs * x == z && y % qs == 0)  {f = y / qs;}
    else { f = 0; Success = false;}
    require Success;
    return f;
}

function identity(uint256 x) returns uint256 
{
    return x;
}

// Set constant withdrawal parameters.
function constantsForWithdrawal(env env2, address pool){
    setConstants_wmn_only(env2, pool);
}

// Set withdrawal parameters (w,m,n) to constants.
function setConstants_wmn_only(env env1, address pool){
    uint256 w = 0;
    uint256 m = 2000;
    uint256 n = 2500;
    address epv = _externalProtectionVault(env1);  

    require w == PoolCol.tokenUserBalance(pool, epv);
    require m == PoolCol.getPoolDataTradingFee(pool);
    require n == networkSettings.withdrawalFeePPM(env1);
}


////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

rule invariantValidPoolAfterTrade(method f)
filtered{f -> tradeLikeMethod(f)}
{
    env e;
    calldataarg args;
    address token = tokenA;

    require !PoolCol.isPoolValid(token) => _poolCollection(token) == 0;
        f(e,args);
    assert !PoolCol.isPoolValid(token) => _poolCollection(token) == 0;
}


rule invariantValidPoolAfterDeposit(method f)
filtered{f -> depositLikeMethod(f)}
{
    env e;
    calldataarg args;
    address token = tokenA;
    
    require !PoolCol.isPoolValid(token) => _poolCollection(token) == 0;
    
    f(e,args);
    
    assert !PoolCol.isPoolValid(token) => _poolCollection(token) == 0;
}


// Conversion to pool tokens from underlying and vice-versa are reciprocal actions.
// Note that the functions are using mulDivF, mulDivC which are summarized via simpleMulDiv(x,y,z).
rule underlyingToPTinverse(uint amount)
{
    env e;
    address token = tokenA;
    address PT = ptA;

    require PoolCol.poolToken(token) == PT;

    uint256 a = PoolCol.poolTokenToUnderlying(e, token, amount);
    uint256 b = PoolCol.underlyingToPoolToken(e, token, a);

    uint256 c = BNTp.poolTokenToUnderlying(e, amount);
    uint256 d = BNTp.underlyingToPoolToken(e, c);
    
    assert b == amount && d == amount, "Calculations are not reciprocal";
}


rule underlyingToPTmono(uint amount1, uint amount2)
{
    env e;
    address token = tokenA;
    address PT = ptA;

    require PoolCol.poolToken(token) == PT;
    uint256 a = PoolCol.underlyingToPoolToken(e, token, amount1);
    uint256 b = PoolCol.underlyingToPoolToken(e, token, amount2);
    
    assert amount1 > amount2 => a > b, "Not monotonic";
}

// Verify the proper registration details in a withdrawal request.
rule checkInitWithdraw(uint amount, address poolToken)
{
    env e;
    address token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            token == ptA.reserveToken(e) &&
            tokenInPoolCollection(token, PoolCol));

    require poolToken == ptBNT =>
            (token == bnt && token == ptBNT.reserveToken(e));

    uint id = initWithdrawal(e, poolToken, amount);

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

// User cannot cancel a withdrawal request twice.
rule noDoubleCanceling(uint amount, address poolToken)
{
    env e;
    address token = PendWit.returnToken(poolToken);

    require poolToken == ptBNT <=> bnt == token;

    require poolToken != ptBNT =>
            (poolToken == ptA && token == tokenA && 
            tokenInPoolCollection(token, PoolCol));
    
    uint id = initWithdrawal(e, poolToken, amount);
    cancelWithdrawal(e, id);
    cancelWithdrawal@withrevert(e, id);
    assert lastReverted;
}

// Verified
rule tradeA2BLiquidity(uint amount, bool byTarget)
{
    env e;
    uint256 maxMinAmount;
    uint256 deadline;
    address beneficiary = e.msg.sender;
    address tknA = tokenA;
    address tknB = tokenB;
    uint256 deltaA;
    uint256 deltaB; 

    require e.msg.sender != masVault;

    uint128 tknALiq1 = PoolCol.getPoolDataBaseTokenLiquidity(tknA);
    uint128 tknBLiq1 = PoolCol.getPoolDataBaseTokenLiquidity(tknB);
    uint256 bntBalance1 = bnt.balanceOf(e, e.msg.sender);

    if(byTarget) {
        deltaA = tradeByTargetAmount(e, tknA, tknB,
                amount, maxMinAmount, deadline, beneficiary);
        deltaB = amount; }
    else {
        deltaB = tradeBySourceAmount(e, tknA, tknB,
                amount, maxMinAmount, deadline, beneficiary); 
        deltaA = amount; }

    uint128 tknALiq2 = PoolCol.getPoolDataBaseTokenLiquidity(tknA);
    uint128 tknBLiq2 = PoolCol.getPoolDataBaseTokenLiquidity(tknB);
    uint256 bntBalance2 = bnt.balanceOf(e, e.msg.sender);

    assert tknALiq2 == deltaA + tknALiq1, "Source token liquidity in the pool
            didn't increase as expected";
   
    assert tknBLiq1 == deltaB + tknBLiq2, "Target token liquidity in the pool
            didn't decrease as expected";
    
    assert bntBalance1 >= bntBalance2, "Trader cannot gain BNT through the trade";
    
    assert PoolCol.networkFeePPM(e) == 0 => bntBalance2 == bntBalance1,
            "When there are no fees, trade BNT balance stays intact"; 
}

 
// Verified
rule tradeBntLiquidity(uint amount)
{
    env e;
    uint256 maxSourceAmount = max_uint;
    uint256 deadline;
    address beneficiary = e.msg.sender;
    address tknA = tokenA;
    address tknB = tokenB;
    require PoolCol.defaultTradingFeePPM() <= 10000;

    require e.msg.sender != masVault;
    // Assuming both tokens are in the same poolCollection
    require _poolCollection(tknA) == PoolCol;

    require _poolCollection(tknB) == PoolCol;

    uint128 bntLiqA1 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB1 = PoolCol.getPoolDataBntTradingLiquidity(tknB);
    uint256 balanceA1 = tokenA.balanceOf(e, e.msg.sender);
    uint256 balanceB1 = tokenB.balanceOf(e, e.msg.sender);

    require balanceA1 <= 10000000000;

    uint amountPaid = tradeByTargetAmount(e, tknA, tknB,
        amount, maxSourceAmount, deadline, beneficiary);

    uint128 bntLiqA2 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB2 = PoolCol.getPoolDataBntTradingLiquidity(tknB);
    uint256 balanceA2 = tokenA.balanceOf(e, e.msg.sender);
    uint256 balanceB2 = tokenB.balanceOf(e, e.msg.sender);

    assert bntLiqA2 <= bntLiqA1 && bntLiqB1 <= bntLiqB2 , 
        "BNT liquidites in the source and target pools 
        must decrease and increase respectively";

    assert balanceB1 + amount == balanceB2 , "Trader must receive his tokens";
    
    assert balanceA1 - amountPaid == balanceA2, "Trader must pay tokens";
}

// Pool tokens are non-tradeable in Bancor Network. with assumption that pool is valid
rule untradeablePT(address trader, address poolToken, uint amount, bool TKN_2_PT)
{
    env e;
    address token;
    uint maxSourceAmount;
    uint256 deadline;

    require poolToken == ptBNT || poolToken == ptA;
    // This invariant needs to be verified first.
    // Without this invariant, trade can be successful.
    requireInvariant validPool(poolToken);
    require !PoolCol.isPoolValid(poolToken);

    if (TKN_2_PT) {
        tradeByTargetAmount@withrevert
                (e, token, poolToken, amount, maxSourceAmount, deadline, trader);
    }
    else {
        tradeByTargetAmount@withrevert
                (e, poolToken, token, amount, maxSourceAmount, deadline, trader);
    }

    assert lastReverted;
}


// assumption for untradeablePT
invariant validPool(address token)
    !PoolCol.isPoolValid(token) => _poolCollection(token) == 0
    filtered{f -> !depositLikeMethod(f) && !tradeLikeMethod(f)}


// Trading should never change the amount of pool tokens for any user.
rule afterTradingPTBalanceIntact(address trader, uint amount)
{
    env e;
    address tknA;
    address tknB;
    address poolToken;
    uint maxSourceAmount;
    uint256 deadline;
    uint256 balancePT1;
    uint256 balancePT2;

    require poolToken == ptBNT || poolToken == ptA;
    // Without this require, a counter example, in which one of the 
    // trade tokens is the pool token, is possible.
    require tknA != poolToken && tknB != poolToken;
    // According to sanity check, this is redundant.
    require trader != _masterVault(e);

    if (poolToken == ptBNT)
        { balancePT1 = ptBNT.balanceOf(e, trader); }
    else
        { balancePT1 = ptA.balanceOf(e, trader); }

    tradeByTargetAmount(e, tknA, tknB, amount, maxSourceAmount, deadline, trader);
    
    if (poolToken == ptBNT)
        { balancePT2 = ptBNT.balanceOf(e, trader); }
    else
        { balancePT2 = ptA.balanceOf(e, trader); }

    assert balancePT2 == balancePT1;
}

// It is always possible to cancel a withdrawal request (without time limit).
rule cancellingAlwaysPossible(address poolToken, uint256 amount)
{
    env e;

    uint  id = initWithdrawal(e, poolToken, amount);
    cancelWithdrawal@withrevert(e, id);

    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}


// After initiating a withdrawal, the user must hand over his PTs.
rule RequestRegisteredForValidProvider(uint tokenAmount)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;
    address provider = e.msg.sender;
    require provider != PendWit;
    setupTokenPoolCol(e, token, poolToken);

    uint balance1 = ptA.balanceOf(e, provider);
    
    uint id = initWithdrawal(e, poolToken, tokenAmount);
    
    uint balance2 = ptA.balanceOf(e, provider);

    assert balance1 - balance2 == tokenAmount;
}


// No user can withdraw twice staked BNTs.
rule noDoubleWithdrawalBNT(uint256 id, uint amount)
{
    env e;
     // Set withdrawal request id
    address provider;
    address poolToken;
    address reserveToken;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);

    // Require consistency
    require provider == e.msg.sender;
    require poolToken == ptBNT;
    require poolTokenAmount == amount;
    require reserveToken == bnt;
    require ptBNT.reserveToken(e) == bnt;
    
    uint256 withAmount = withdraw(e, id);

    address provider2;
    address poolToken2;
    address reserveToken2;
    uint32 createdAt2;
    uint256 poolTokenAmount2;
    uint256 reserveTokenAmount2;
    provider2, poolToken2, reserveToken2, createdAt2, poolTokenAmount2, 
            reserveTokenAmount2 = PendWit.withdrawalRequest(id);
    
    assert provider2 == 0;
    // Revert is guaranteed via verifiying the rule 'doubleWithdrawHelper'.
}

// A withdraw execution must revert if the request's provider is the zero address.
rule doubleWithdrawHelper(uint256 id)
{
    env e;
    address provider;
    address poolToken;
    address reserveToken;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;
    provider, poolToken, reserveToken, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);

    withdraw@withrevert(e, id);
    assert provider == 0 => lastReverted, 
            "Request to withdraw must revert for zero address provider";
}
    

// A provider of BNT must deposit his tokens and get his pool tokens.
// Also, upon requesting to withdraw, the same gained pool tokens must be given 
// back to the protocol.
rule depositBntIntegrity(uint256 amount)
{
    env e;
    require validUser(e, e.msg.sender);
    require ptBNT.reserveToken(e) == bnt;
    require VbntGovern._token() == _vbnt(e);
    require BntGovern._token() == _bnt(e);

    // Balances before deposit
    uint balancePT1 = ptBNT.balanceOf(e, e.msg.sender);
    uint balanceBNT1 = bnt.balanceOf(e, e.msg.sender);
    // Deposit (amount) BNT to pool.
    uint amountPT = deposit(e, bnt, amount);
    // Balances after deposit, before withdrawal.
    uint balancePT2 = ptBNT.balanceOf(e, e.msg.sender);
    uint balanceBNT2 = bnt.balanceOf(e, e.msg.sender);

    assert balanceBNT2 == balanceBNT1 - amount, 
            "User's BNT balance did not decrease as expected";
    assert balancePT2 == balancePT1 + amountPT, 
            "User's PT balance did not increase as expected";

    // Request to withdraw.
    uint id = initWithdrawal(e, ptBNT, amountPT);
    // Balances after withdraw request.
    uint balancePT3 = ptBNT.balanceOf(e, e.msg.sender);
    uint balanceBNT3 = bnt.balanceOf(e, e.msg.sender);

    assert balancePT3 == balancePT1 , "User's PT balance changed unexpectedly";
}


// A provider of any TKN must deposit his tokens and get his pool tokens.
// Also, upon requesting to withdraw, the same gained pool tokens must be given 
rule depositTknIntegrity(uint256 amount)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;

    require validUser(e, e.msg.sender);
    require ptA.reserveToken(e) == token;
    setupTokenPoolCol(e, token, poolToken);
    require collectionByPool(token) == PoolCol;

    // Balances before deposit
    uint balancePT1 = ptA.balanceOf(e, e.msg.sender);
    uint balanceTKN1 = tokenA.balanceOf(e, e.msg.sender);
    // Deposit (amount) BNT to pool.
    uint amountPT = deposit(e, token, amount);
    // Balances after deposit, before withdrawal.
    uint balancePT2 = ptA.balanceOf(e, e.msg.sender);
    uint balanceTKN2 = tokenA.balanceOf(e, e.msg.sender);
    
    assert balanceTKN2 == balanceTKN1 - amount, 
            "User's BNT balance did not decrease as expected";
    assert balancePT2 == balancePT1 + amountPT, 
            "User's PT balance did not increase as expected";

    // Request to withdraw.
    uint id = initWithdrawal(e, poolToken, amountPT);
    // Balances after withdraw request.
    uint balancePT3 = ptA.balanceOf(e, e.msg.sender);
    uint balanceTKN3 = tokenA.balanceOf(e, e.msg.sender);

    assert balancePT3 == balancePT1 , "User's PT balance changed unexpectedly";
}

// The sum of balances after a trade must not change.
// Balance (trader) + Balance (vault) = const.
rule afterTradeSumOfTokenBalanceIntact(address tknA, address tknB, uint amount)
{
    env e;
    address trader = e.msg.sender;
    address vault = _masterVault(e);
    require tknA == bnt || tknA == tokenA || tknA == tokenB;
    require tknB == bnt || tknB == tokenA || tknB == tokenB;
    require validUser(e,trader);

    uint256 traderBalanceA1 = PoolCol.tokenUserBalance(tknA, trader);
    uint256 traderBalanceB1 = PoolCol.tokenUserBalance(tknB, trader);
    uint256 vaultBalanceA1 = PoolCol.tokenUserBalance(tknA, vault);
    uint256 vaultBalanceB1 = PoolCol.tokenUserBalance(tknB, vault);

    uint maxSourceAmount;
    uint deadline;

    tradeByTargetAmount(e, tknA, tknB,
        amount, maxSourceAmount, deadline, trader);

    uint256 traderBalanceA2 = PoolCol.tokenUserBalance(tknA, trader);
    uint256 traderBalanceB2 = PoolCol.tokenUserBalance(tknB, trader);
    uint256 vaultBalanceA2 = PoolCol.tokenUserBalance(tknA, vault);
    uint256 vaultBalanceB2 = PoolCol.tokenUserBalance(tknB, vault);

    assert traderBalanceA2 + vaultBalanceA2 == 
            traderBalanceA1 + vaultBalanceA1,
            "Source token total balance isn't conserved after trade";

    assert traderBalanceB2 + vaultBalanceB2 == 
            traderBalanceB1 + vaultBalanceB1,
            "Target token total balance isn't conserved after trade";

}

// A provider of BNT must recieve pool tokens from the protocol.
rule depositBNTtransferPTsToProvider(address provider, uint amount)
{
    env e;
    address PT = _bntPoolToken(e);
    address protocol = _bntPool(e);
    require validUser(e, provider);

    uint256 providerPTBntBalance1 = PoolCol.tokenUserBalance(PT, provider);
    uint256 networkPTBntBalance1 = PoolCol.tokenUserBalance(PT, protocol);
    uint256 PTtotalSupply1 =  PendWit.poolTotalSupply(PT);

        uint amountPT = depositFor(e,provider, _bnt(e), amount);

    uint256 providerPTBntBalance2 = PoolCol.tokenUserBalance(PT, provider);
    uint256 networkPTBntBalance2 = PoolCol.tokenUserBalance(PT, protocol);
    uint256 PTtotalSupply2 =  PendWit.poolTotalSupply(PT);

    assert networkPTBntBalance2 + amountPT == networkPTBntBalance1,
            "Protocol should transfer its pool tokens to provider";

    assert providerPTBntBalance1 + amountPT == providerPTBntBalance2,
            "The amount of PTs minted to provider is wrong";

    assert PTtotalSupply1 == PTtotalSupply2, 
            "Total supply of BNT pool tokens should not change";
}

rule tradeTargetSourceInverse(uint amount)
{
    env e;
    address tknA = tokenA;
    address tknB = tokenB;
    uint maxSourceAmount = max_uint;
    uint minReturnAmount = 1;
    uint deadline = max_uint;
    address trader = e.msg.sender;
    require _poolCollection(tknA) == PoolCol;
    require _poolCollection(tknB) == PoolCol;
    require amount > 0;

    storage initialStorage = lastStorage;

rule tradeTargetSourceInverse(uint amount)
{
    env e;
    address tknA = tokenA;
    address tknB = tokenB;
    uint maxSourceAmount = max_uint;
    uint minReturnAmount = 1;
    uint deadline = max_uint;
    address trader = e.msg.sender;
    require _poolCollection(tknA) == PoolCol;
    require _poolCollection(tknB) == PoolCol;
    require amount > 0;

    storage initialStorage = lastStorage;

    uint256 amountPaid = tradeByTargetAmount(e, tknA, tknB,
        amount, maxSourceAmount, deadline, trader);

    require amountPaid > 0;

    uint256 amountBack = tradeBySourceAmount(e, tknA, tknB,
        amountPaid, minReturnAmount, deadline, trader) at initialStorage;

    //assert false;
    assert amountBack == amount;
}









// STATUS - verified
// No pool collection for non-valid pool.
invariant noPoolNoParty1(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == registerPoolCollection(address).selector 
                        || f.selector == unregisterPoolCollection(address).selector 
                        || f.selector == createPools(address[], address).selector
    }

// STATUS - verified
invariant noPoolNoParty2(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == depositFor(address, address, uint256).selector
                        || f.selector == deposit(address, uint256).selector
                        // || f.selector == depositForPermitted(address, address, uint256, uint256, uint8, bytes32, bytes32).selector
                        // || f.selector == depositPermitted(address, uint256, uint256, uint8, bytes32, bytes32).selector 
    }


// STATUS - verified
invariant noPoolNoParty3(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == initWithdrawal(address, uint256).selector
                        || f.selector == cancelWithdrawal(uint256).selector
    }


// STATUS - verified
invariant noPoolNoParty4(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == withdraw(uint256).selector}
    

// STATUS - verified
invariant noPoolNoParty5(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == tradeByTargetAmount(address, address, uint256, uint256, uint256, address).selector }


// STATUS - verified
invariant noPoolNoParty6(address token)
    !PoolCol.isPoolValid(token) => collectionByPool(token) == 0
    filtered { f -> f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
                        // || f.selector == withdrawNetworkFees(address).selector
                        // || f.selector == pause().selector
                        // || f.selector == resume().selector
    }




// STATUS - verified
// Check functions for non-reentracncy.
// rule reentrancyCheck1(env e, method f) 
// filtered { f -> f.selector == registerPoolCollection(address).selector 
//                     || f.selector == unregisterPoolCollection(address).selector
//                     || f.selector == createPools(address[], address).selector
//                     || f.selector == migratePools(address[], address).selector 
// } {                        
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// STATUS - verified
// rule reentrancyCheck2(env e, method f)
// filtered { f -> f.selector == depositFor(address, address, uint256).selector
//                         || f.selector == deposit(address, uint256).selector 
// } {                         
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// // STATUS - verified
// rule reentrancyCheck3(env e, method f) 
// filtered { f -> f.selector == initWithdrawal(address, uint256).selector
//                         || f.selector == cancelWithdrawal(uint256).selector
// } {                         
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// // STATUS - verified
// rule reentrancyCheck4(env e, method f) 
// filtered { f -> f.selector == withdraw(uint256).selector }
// {                         
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// // STATUS - verified
// rule reentrancyCheck511(env e, method f) 
// filtered { f -> f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector
// } {                         
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }


// // STATUS - verified
// rule reentrancyCheck521(env e, method f) 
// filtered { f -> f.selector == tradeByTargetAmount(address, address, uint256, uint256, uint256, address).selector
// }
// {                          
//     uint256 status = _status(e);
//     require status == 2;
    
//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// // STATUS - verified
// rule reentrancyCheck6(env e, method f) 
// filtered { f -> f.selector == flashLoan(address, uint256, address, bytes).selector
//                         || f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
// } {                         
//     uint256 status = _status(e);
//     require status == 2;

//     calldataarg args;
//     f@withrevert(e, args);
//     assert lastReverted, "Mortal soul cannot get God's power!";
// }

// STATUS - verified
// Only user with admin role can call certain functions
// rule almightyAdmin1(env e, method f) filtered 
// { f -> f.selector == registerPoolCollection(address).selector 
//         || f.selector == unregisterPoolCollection(address).selector 
//         || f.selector == createPools(address[], address).selector 
// } {
//     bool roleBefore = hasRole(roleAdmin(), e.msg.sender);
    
//     calldataarg args;
//     f@withrevert(e, args);

//     bool isReverted = lastReverted;

//     assert !roleBefore => isReverted, "With great power comes great responsibility";
// }



// STATUS - verified
// Only user with concrete role can call concrete functions.
// rule almightyAdmin2(method f, env e) filtered { f -> f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
//                                             || f.selector == withdrawNetworkFees(address).selector
//                                             || f.selector == pause().selector
//                                             || f.selector == resume().selector} {
//     calldataarg args;
//     f@withrevert(e, args);

//     bool isReverted = lastReverted;

//     assert  (!isReverted && (f.selector == pause() .selector
//                                 || f.selector == resume().selector))
//                 => hasRole(roleEmergencyStopper(), e.msg.sender), "With great power comes great requestFunding/renounceFunding";
//     assert  (!isReverted && f.selector == withdrawNetworkFees(address).selector)
//                 => hasRole(roleNetworkFeeManager(), e.msg.sender), "With great power comes great mint";
//     assert  (!isReverted && f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector)
//                 => hasRole(roleMigrationManager(), e.msg.sender), "With great power comes great burnFromVault";
// }



// STATUS - verified
// There is no way to call certain functions when network is paused.
// rule whenPausedNothingToDo2(env e, method f) 
// filtered { f -> f.selector == depositFor(address, address, uint256).selector
//                         || f.selector == deposit(address, uint256).selector
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }

// // STATUS - verified
// rule whenPausedNothingToDo3(env e, method f) 
// filtered { f -> f.selector == initWithdrawal(address, uint256).selector
//                         || f.selector == cancelWithdrawal(uint256).selector
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }

// // STATUS - verified
// rule whenPausedNothingToDo4(env e, method f) 
// filtered { f -> f.selector == withdraw(uint256).selector}
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }


// rule whenPausedNothingToDo512(env e, method f) 
// filtered { f -> f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector              
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }

// rule whenPausedNothingToDo521(env e, method f) 
// filtered { f -> f.selector == tradeByTargetAmount(address, address, uint256, uint256, uint256, address).selector
//                             }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }


// rule whenPausedNothingToDo61(env e, method f) 
// filtered { f -> f.selector == flashLoan(address, uint256, address, bytes).selector                       
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }

// rule whenPausedNothingToDo62(env e, method f) 
// filtered { f -> f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector             
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }

// rule whenPausedNothingToDo63(env e, method f) 
// filtered { f -> f.selector == withdrawNetworkFees(address).selector
//     }
// {
//     require isPaused();

//     calldataarg args;
//     f@withrevert(e, args);

//     assert lastReverted, "Frozen!";
// }


// STATUS - proved
// `flashLoan()` doesn't decrease network's balance (native or token). 
// rule flashLoanCompleteness(env e){
//     address token;
//     uint256 amount;
//     address recipient;
//     bytes calldata;

//     require token == tokenA || token == tokenB;

//     uint256 nativeBalanceBefore = ethBalance();

//     uint256 tokenBalanceBefore;
//     if(token == tokenA){
//         tokenBalanceBefore = tokenA.balanceOf(e, currentContract);
//     } else {
//         tokenBalanceBefore = tokenB.balanceOf(e, currentContract);
//     }

//     flashLoan(e, token, amount, recipient, calldata);

//     uint256 nativeBalanceAfter = ethBalance();
    
//     uint256 tokenBalanceAfter;
//     if(token == tokenA){
//         tokenBalanceAfter = tokenA.balanceOf(e, currentContract);
//     } else {
//         tokenBalanceAfter = tokenB.balanceOf(e, currentContract);
//     }

//     assert nativeBalanceBefore <= nativeBalanceAfter && tokenBalanceBefore <= tokenBalanceAfter, "Flash is a cheater!";
// }
