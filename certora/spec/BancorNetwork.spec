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

    isPoolValid(address) returns (bool) envfree
    depositFor(address, address, uint256) returns (uint256) 
    deposit(address, uint256) returns (uint256) 

    depositForPermitted(address, address, uint256, uint256, 
            uint8, bytes32, bytes32) returns (uint256) 

    depositPermitted(address, uint256, uint256,
            uint8, bytes32, bytes32) returns (uint256) 

    _withdrawContextId(uint256, address) returns(bytes32)

    // Pool collection
    depositFor(bytes32, address, address, uint256) returns (uint256) => DISPATCHER(true)
    tradeByTargetAmount(bytes32, address, address, uint256, uint256)
                returns (uint256, uint256, uint256) => DISPATCHER(true)
    tradeBySourceAmount(bytes32, address, address, uint256, uint256)
                returns (uint256, uint256, uint256) => DISPATCHER(true)
    poolType() returns (uint16) => DISPATCHER(true)
    poolCount() returns (uint256) => DISPATCHER(true)
    createPool(address) => DISPATCHER(true)
    withdraw(bytes32, address, address, uint256) returns (uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    poolTokenToUnderlying(address, uint256) returns (uint256) => DISPATCHER(true)
    underlyingToPoolToken(address, uint256) returns (uint256) => DISPATCHER(true)
    PoolCol.getPoolDataTradingFee(address) returns (uint32) envfree
    PoolCol.getPoolDataStakedBalance(address) returns (uint256) envfree
    PoolCol.getPoolDataBntTradingLiquidity(address) returns(uint128) envfree
    PoolCol.getPoolDataBaseTokenLiquidity(address) returns(uint128) envfree
    PoolCol.poolToken(address) returns (address) envfree
    PoolCol.defaultTradingFeePPM() returns (uint32) envfree
    PoolCol.tokenUserBalance(address, address) returns (uint256) envfree
    PoolCol.isPoolValid(address) returns(bool) envfree

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
    reserveToken() returns (address) => DISPATCHER(true)
    mulDivF(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDiv(x,y,z)
    mulDivC(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDiv(x,y,z)
    hasRole(bytes32, address) returns(bool) envfree
    roleAdmin() returns(bytes32) envfree
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

// Hook to havoc the total sum of pool tokens.
//hook Sstore PendWit._withdrawalRequests[KEY address user].poolTokenAmount uint256 balance (uint256 old_balance) STORAGE {
//    havoc sumRequestPoolTokens assuming forall address poolToken.
//    ((requestPoolTokenGhost(id) == poolToken) ?
//    sumPTbalances@new(poolToken) == sumPTbalances@old(poolToken) + balance - old_balance :
//    sumPTbalances@new(poolToken) == sumPTbalances@old(poolToken));
//}

definition depositLikeMethod(method f) returns bool = 
        f.selector == depositFor(address, address, uint256).selector ||
        f.selector == deposit(address, uint256).selector ||

        f.selector == depositForPermitted(address, address, uint256, uint256, 
            uint8, bytes32, bytes32).selector ||

        f.selector == depositPermitted(address, uint256, uint256, 
            uint8, bytes32, bytes32).selector ;  

definition tradeLikeMethod(method f) returns bool = 
        f.selector == 
        tradeBySourceAmount(address, address, uint256, uint256, uint256, address)
        .selector ||
        
        f.selector == 
        tradeByTargetAmount(address, address, uint256, uint256, uint256, address)
        .selector ||

        f.selector == 
        tradeBySourceAmountPermitted(address, address, uint256, uint256, uint256, address,
        uint8, bytes32, bytes32).selector ||

        f.selector == 
        tradeByTargetAmountPermitted(address, address, uint256, uint256, uint256, address,
        uint8, bytes32, bytes32).selector;

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

////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////

invariant whiteListedToken(env e, address token)
    isTokenWhitelisted(e, token)

// Failed:
// https://vaas-stg.certora.com/output/41958/dd6b365803a568c539cd/?anonymousKey=68692b3845ee183ded9e5145dc37f63e8e041e73
invariant validPool(address token)
    !isPoolValid(token) => _poolCollection(token) == 0
    filtered{f -> !depositLikeMethod(f) && !tradeLikeMethod(f)}

//https://vaas-stg.certora.com/output/41958/dcdc01d1ce1740249872/?anonymousKey=42f1ef1a1e0a739ed3b34b06109fae02ffb6abcb
invariant poolLinkPoolCollection(address pool)
    collectionByPool(pool) == PoolCol <=> _poolCollection(pool) == PoolCol


// Maybe should be verified in two steps:
// sum(Requests PT) <= sum(balances PT)
// sum(balances) <= totalSupply
invariant withdrawalRequestPTsSolvency(address token)
    sumRequestPoolTokens(token) <= PendWit.poolTotalSupply(token)
    {
        preserved
        {
            require token == ptA;
        }
    }

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

// Verified
// https://vaas-stg.certora.com/output/41958/3724e32fa452a367a6c5/?anonymousKey=e38bd0786d57db27ef993a6b3b26219b73504bc1
// I'm splitting the validPool invariant to several rules with different functions.
rule invariantValidPoolAfterTrade(method f)
filtered{f -> tradeLikeMethod(f)}
{
    env e;
    calldataarg args;
    address token = tokenA;

    require !isPoolValid(token) => _poolCollection(token) == 0;
        f(e,args);
    assert !isPoolValid(token) => _poolCollection(token) == 0;
}

// Verified
// https://vaas-stg.certora.com/output/41958/b3ed87cf62c965ec924d/?anonymousKey=1ee88cf59667a1dc5bfbc2a1a3c395199ef96df8
// I'm splitting the validPool invariant to several rules with different functions.
rule invariantValidPoolAfterDeposit(method f)
filtered{f -> depositLikeMethod(f)}
{
    env e;
    calldataarg args;
    address token = tokenA;
    
    require !isPoolValid(token) => _poolCollection(token) == 0;
        f(e,args);
    assert !isPoolValid(token) => _poolCollection(token) == 0;
}


// Conversion to pool tokens from underlying and vice-versa
// are reciprocal actions.
// Verified
// https://vaas-stg.certora.com/output/41958/9a6c07ab6c77e6a76436/?anonymousKey=77a9bd6c46b90f52102fb79975973e374ed60069
// Note that the functions are using mulDivF, mulDivC which are summarized
// via simpleMulDiv(x,y,z).
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

// Verified
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
// Verified
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
// Verified
rule noDoubleCancelling(uint amount, address poolToken)
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
// https://vaas-stg.certora.com/output/41958/9ea0d961e2d4a84f5713/?anonymousKey=c4babec51f6bffd9468718a03a3736e21e5f348c
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
    
    assert networkSettings.networkFeePPM(e) ==0 => bntBalance2 == bntBalance1,
            "When there are no fees, trade BNT balance stays intact"; 
}

// 
// Verified
// https://vaas-stg.certora.com/output/41958/6569e23d4965197f94ff/?anonymousKey=50bc6de510716037ac71bb0f578a3b6262e6bc93
rule tradeBntLiquidity(uint amount)
{
    env e;
    uint256 maxSourceAmount = max_uint;
    uint256 deadline ;
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

    uint amountPaid = tradeByTargetAmount(e, tknA, tknB,
        amount, maxSourceAmount, deadline, beneficiary);

    uint128 bntLiqA2 = PoolCol.getPoolDataBntTradingLiquidity(tknA);
    uint128 bntLiqB2 = PoolCol.getPoolDataBntTradingLiquidity(tknB);
    uint256 balanceA2 = tokenA.balanceOf(e, e.msg.sender);
    uint256 balanceB2 = tokenB.balanceOf(e, e.msg.sender);

    assert bntLiqA2 <= bntLiqA1 && bntLiqB1 <= bntLiqB2 , 
        "BNT liquidites in the source and target pools 
        must decrease and increase respectively";

    assert balanceA1 - amountPaid == balanceA2, "Trader must pay tokens";
    
    assert balanceB1 + amount == balanceB2 , "Trader must receive his tokens";
}

// Pool tokens are non-tradeable in Bancor Network.
// Verified (with require invariant):
// https://vaas-stg.certora.com/output/41958/a71106a331cf29d55991/?anonymousKey=204ceafea81b946cee50bb1d75cb333f6f603c8d
// Failed (without require invariant):
// https://vaas-stg.certora.com/output/41958/2ef71569f6fcf1f7a5fa/?anonymousKey=e07fa92b869e3eb90b59f9f46c78119111c722c8
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
    require !isPoolValid(poolToken);

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

// Trading should never change the amount of pool tokens for any user.
// Verified
// https://vaas-stg.certora.com/output/41958/48a134f59ef6d5b20e2d/?anonymousKey=7a032229bdada100875977853144ccc6bea3c01d
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
// Verified *
// *Lines 395-396 in PendingWithdrawals.sol can lead to revert, but remove should
// always be successful (when id exists):
// https://vaas-stg.certora.com/output/41958/39449221027bb1ee7609/?anonymousKey=a0bca7abb39ca7c93fd9d4370cf1402d2bcdbb73
rule cancellingAlwaysPossible(address poolToken, uint256 amount)
{
    env e;

    uint  id = initWithdrawal(e, poolToken, amount);
    cancelWithdrawal@withrevert(e, id);

    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}

// After initiating a withdrawal, the user must hand over his PTs.
// Verified
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

// Checks which functions change the master vault balance.
// This is the first run:
// https://vaas-stg.certora.com/output/41958/cd16c503a796770a2312/?anonymousKey=1c49f7b5fa0def76abb557430f90079823dcc1e3
// This will help to modify the preserved block in the future.
rule whoChangedMasterVaultBalance(method f)
filtered{f -> f.selector != withdraw(uint).selector && !depositLikeMethod(f)}
{
    env e;
    calldataarg args;
    address Vault = _masterVault(e);

    uint balanceTKN1 = tokenA.balanceOf(e, Vault);
    uint balanceBNT1 = bnt.balanceOf(e, Vault);
        f(e,args);
    uint balanceTKN2 = tokenA.balanceOf(e, Vault);
    uint balanceBNT2 = bnt.balanceOf(e, Vault);

    assert balanceBNT1 == balanceBNT2 &&
            balanceTKN1 == balanceTKN2;
}

// No user can withdraw twice staked BNTs.
// We actually verify that the request registered provider after withdrawal is zero.
// Verified
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
// Verified
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
    assert provider ==0 => lastReverted, 
            "Request to withdraw must revert for zero address provider";
}
    
// No user can withdraw twice staked tokens.
// Is reachable.
// Currently hard-stops.
// Note : I saved a call to initWithdrawal to avoid timeouts.
// The require statements were added instead (and were verified
// in the checkInitWithdraw rule).
rule noDoubleWithdrawalTKN(uint256 ptAmount, uint id)
{
    env e;
    address poolToken = ptA;
    address token = tokenA;
    require ptA.reserveToken(e) == token;
    setupTokenPoolCol(e, token, poolToken);
    require collectionByPool(token) == PoolCol;

    // Set withdrawal request id
    address provider;
    address poolToken2;
    address reserveToken2;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;
    provider, poolToken2, reserveToken2, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);
    // Require consistency
    require provider == e.msg.sender;
    require poolToken2 == poolToken;
    require ptAmount == poolTokenAmount;
    require reserveToken2 == token;

    // Withdraw:
    constantsForWithdrawal(e, token);
    uint256 withAmount = withdraw(e, id);
    withdraw@withrevert(e, id);
    assert lastReverted;
}

// A provider of BNT must deposit his tokens and 
// get his pool tokens.
// Also, upon requesting to withdraw, the same gained pool tokens must be given 
// back to the protocol.
// Verified
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

// A provider of any TKN must deposit his tokens and 
// get his pool tokens.
// Also, upon requesting to withdraw, the same gained pool tokens must be given 
// back to the protocol.
// Verified
//https://vaas-stg.certora.com/output/41958/5e2069df2a8c46f91103/?anonymousKey=2116b7dac8dbe7a77a68c082c2260df6bff713d8
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
// Pass sanity
// https://vaas-stg.certora.com/output/41958/3bdcf78e4cc6513c9a30/?anonymousKey=50637c4aa491deb6f7c2855e1feb5b0a5b8b843a
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
// Verified
// https://vaas-stg.certora.com/output/41958/fab1163326e083b448b9/?anonymousKey=6762bcb099e85bb3a57d370d7769deb923d31f1b
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

// Can some trader prevent me from taking my money?
// Hard-stops
rule tradeFrontRunsWithdrawal(uint amount, bool sourceA)
{
    env e;
    address tkn = tokenA;
    address tkn2;
    address provider = e.msg.sender;
    address trader;
    address PT = ptA;
    uint256 maxSourceAmount = max_uint;
    uint256 deadline = max_uint;
    uint256 amountPT;
    
    require tkn2 == tokenB || tkn2 == _bnt(e);
    require validUser(e, provider);
    require PT == PoolCol.poolToken(tkn);
    require ptA.reserveToken(e) == tkn;
    require validUser(e, trader);
    require trader != provider;
    require amountPT > 0;
    require PendWit.poolTotalSupply(PT) >= amountPT;

    // Init withdrawal by provider
    uint256 id = initWithdrawal(e, PT, amountPT);
    // For the sake of verification, we allow immediate withdrawal.
    require PendWit.lockDuration() == 0;

    // Trade by some user
    if(sourceA){
        uint256 amountPaid = tradeByTargetAmount(e, tkn, tkn2,
        amount, maxSourceAmount, deadline, trader);
    }
    else {
        uint256 amountPaid = tradeByTargetAmount(e, tkn2, tkn,
        amount, maxSourceAmount, deadline, trader);
    }

    // Request withdrawal
    uint256 amountWith = withdraw@withrevert(e, id);

    assert !lastReverted;
}

// Assuming no trade function.
// Failed:
// https://vaas-stg.certora.com/output/41958/617c4737cc2be61d49d4/?anonymousKey=0d5c26916a572e614b8fcf008b8910957f568e89
rule onlyDepositIncreasePT(method f, address user)
filtered{f -> f.selector != withdraw(uint).selector && !f.isView && !tradeLikeMethod(f)}
{
    env e;
    calldataarg args;
    require validUser(e,user);

    address PT;
    require PT == ptBNT || PT == ptA;

    uint256 balance1 = PoolCol.tokenUserBalance(PT, user);
        f(e,args);
    uint256 balance2 = PoolCol.tokenUserBalance(PT, user);

    assert balance2 > balance1 => depositLikeMethod(f), 
            "Only deposit can increase pool tokens balance";
}

// Verified (needs to check that is sane).
rule withdrawDoesntChangePT(address user)
{
    env e;
    address PT;
    require PT == ptBNT || PT == ptA;
    require validUser(e, user);
 
    uint256 id;
    address provider;
    address poolToken;
    address reserveToken1;
    uint32 createdAt;
    uint256 poolTokenAmount;
    uint256 reserveTokenAmount;

    uint256 balance1;
    uint256 balance2;

    provider, poolToken, reserveToken1, createdAt, poolTokenAmount, 
            reserveTokenAmount = PendWit.withdrawalRequest(id);

    require poolToken == PT;
    if(PT == ptBNT)
    {
        require reserveToken1 == _bnt(e);
        require ptBNT.reserveToken(e) == reserveToken1;
        balance1 = ptBNT.balanceOf(e, user);
    }
    else 
    {
        require reserveToken1 == tokenA;
        require ptA.reserveToken(e) == reserveToken1;
        balance1 = ptA.balanceOf(e, user);
        constantsForWithdrawal(e, reserveToken1);
    }
    
    withdraw(e, id);

    if(PT == ptBNT)
        { balance2 = ptBNT.balanceOf(e, user); }
    else 
        { balance2 = ptA.balanceOf(e, user); }
    
    assert balance1 == balance2,
            "Pool token balance changed unexpectedly";
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
            tokenInPoolCollection(token, PoolCol);
}

// Summary for mulDivF:
// A function which assumes a constant quotient y/z or x/z q (or 1/q).
function constQuotientMulDiv(uint256 x, uint256 y, uint256 z, uint256 q)
returns uint256
{
    uint256 f;
    require z != 0;
    require constQuotient(q);
    return f;
}

// Summary for mulDivF:
// Quotients x/z, y/z are either 0,1,2,3,10 or 1/2, 1/3, 1/10.
// We assume also no division remainders.
function simpleMulDiv(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    // We restrict to no remainders
    // Possible quotients : Qut[q] means that y/z or x/z is q.
    bool Qut0 = ( x ==0 || y ==0) && (f == 0);
    bool Qut1 = ( x == z && f == y ) || ( y == z && f == x );
    bool Qut2 = constQuotient(x, y, z, 2, f);
    bool Qut3 = constQuotient(x, y, z, 3, f);
    bool Qut10 = constQuotient(x, y, z, 10, f);
    bool Qut100 = constQuotient(x, y, z, 100, f);
    bool Qut250 = constQuotient(x, y, z, 250, f);
    bool Qut400 = constQuotient(x, y, z, 400, f);
    bool Qut500 = constQuotient(x, y, z, 500, f);
    bool Qut1000 = constQuotient(x, y, z, 1000, f);
    bool Qut2000 = constQuotient(x, y, z, 2000, f);

    require dontDividebyZero;
    require Qut0 || Qut1 || Qut2 || Qut3 || Qut10 || Qut100 || Qut250 || Qut400 ||
    Qut500 || Qut1000 || Qut2000;
    return f;
}

// Summary for mulDivF:
// quotient y/z is either 0,1,2,3,10 or 1/2, 1/3, 1/10.
// Nothing resticts the value of x/z;
function simpleMulDivIf(uint256 x, uint256 y, uint256 z) returns uint256 
{
    uint f;
    bool dontDividebyZero = z != 0;
    bool Success = true;
    require dontDividebyZero;

    if (x ==0 || y ==0)      {f = 0;}
    else if (y == 2 * z)     {f = 2 * x;}
    else if (y == 3 * z)     {f = 3 * x;}
    else if (y == 10 * z)    {f = 10 * x;}
    else if (2 * y == z && x % 2 == 0)  {f = x / 2;}
    else if (3 * y == z && x % 3 == 0)  {f = x / 3;}
    else if (10 * y == z && x % 10 == 0)    {f = x / 10;}
    else if (y == z)   { f = x;}
    else    {f = 0; Success = false;}

    require Success;
    return f;
}

// Summary for mulDivF:
// quotient y/z is either 0, 1, 2 or half.
function mulDivFactor2(uint256 x,uint256 y, uint256 z) returns uint256 
{
    require z !=0;
    if (x == 0 || y == 0){
        return 0;
    }
    else if (y > z){
        return to_uint256(2 * x);
    }
    else if (y < z){
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











// STATUS - in progress
// No token duplicates in the same pool collection.
// A token can be inside one pool collection only.
// john:
// basic:
invariant lonelyToken(env e, method f, address token, address randToken)
    (isPoolValid(token) && isPoolValid(randToken) && collectionByPool(token) == collectionByPool(randToken)) => token == randToken
    filtered { f -> f.selector != certorafallback_0().selector
                        && (
                            // f.selector == createPool(uint16, address).selector 
                            // || f.selector == migratePools(address[]).selector
                            // || f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
                            // f.selector == setLatestPoolCollection(address).selector
                            // || f.selector == flashLoan(address, uint256, address, bytes).selector
                            // || f.selector == deposit(address, uint256).selector
                            // f.selector == withdraw(uint256).selector
                            f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector
                            || f.selector == addPoolCollection(address).selector 
                            || f.selector == removePoolCollection(address, address).selector
                        )
    }


// STATUS - in progress
// john:
// basic:
// A token can be inside one pool collection only.
invariant lonelyToken2(env e, method f, address token, address randToken)
    isPoolValid(token) && isPoolValid(randToken) && token == randToken => collectionByPool(token) == collectionByPool(randToken)
    filtered { f -> f.selector != certorafallback_0().selector
                        && (
                            // f.selector == createPool(uint16, address).selector 
                            // || f.selector == migratePools(address[]).selector
                            // || f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
                            // f.selector == setLatestPoolCollection(address).selector
                            // || f.selector == flashLoan(address, uint256, address, bytes).selector
                            // || f.selector == deposit(address, uint256).selector
                            // f.selector == withdraw(uint256).selector
                            f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector
                            || f.selector == addPoolCollection(address).selector 
                            || f.selector == removePoolCollection(address, address).selector
                        )
    }


// STATUS - in progress
// john:
// basic:
// check correlation of isPoolValid() in PoolCollection and BancorNetwork
invariant correlationCheck(address token)
    isPoolValid(token) == PoolCol.isPoolValid(token)
    filtered { f -> f.selector != certorafallback_0().selector
                        && (
                            // f.selector == createPool(uint16, address).selector 
                            // || f.selector == migratePools(address[]).selector
                            // || f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector
                            // f.selector == setLatestPoolCollection(address).selector
                            // || f.selector == flashLoan(address, uint256, address, bytes).selector
                            // || f.selector == deposit(address, uint256).selector
                            // f.selector == withdraw(uint256).selector
                            f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector
                            || f.selector == addPoolCollection(address).selector 
                            || f.selector == removePoolCollection(address, address).selector
                        )
    }


// STATUS - in progress
// Pool tokens must be burnt after withdrawal.
// john:
// basic:
rule mustBeBurned(env e) {
    uint256 id;
    address poolToken; uint256 ptToBeBurned; uint256 originalPTAmount;
    bytes32 contextId;

    require contextId == _withdrawContextId(e, id, e.msg.sender);

    uint256 ptBalanceBefore = ptA.balanceOf(e, currentContract);    
    uint256 ptTotalBefore = ptA.totalSupply(e);  

    storage initialStorage = lastStorage;
    
    poolToken, ptToBeBurned, originalPTAmount = PendWit.completeWithdrawal(e, contextId, e.msg.sender, id);
    
    require poolToken != _bntPoolToken(e);
    
    withdraw(e, id) at initialStorage;

    uint256 ptBalanceAfter = ptA.balanceOf(e, currentContract);
    uint256 ptTotalAfter = ptA.totalSupply(e);

    assert ptBalanceBefore == ptBalanceAfter + ptToBeBurned;
    assert ptTotalBefore == ptTotalAfter + ptToBeBurned;
}


// STATUS - in progress
// only bancorNetwork contract can call certain functions
// john:
// basic:
rule reentracncyCheck(env e, method f) filtered { f -> f.selector == addPoolCollection(address).selector 
                                                || f.selector == removePoolCollection(address, address).selector 
                                                || f.selector == setLatestPoolCollection(address).selector
                                                || f.selector == createPool(uint16, address).selector 
                                                || f.selector == createPools(uint16, address[]).selector
                                                || f.selector == migratePools(address[]).selector 
                                                || f.selector == depositFor(address, address, uint256).selector
                                                || f.selector == deposit(address, uint256).selector 
                                                || f.selector == depositForPermitted(address, address, uint256, uint256, uint8, bytes32, bytes32).selector
                                                || f.selector == depositPermitted(address, uint256, uint256, uint8, bytes32, bytes32).selector 
                                                || f.selector == initWithdrawal(address, uint256).selector
                                                || f.selector == initWithdrawalPermitted(address, uint256, uint256, uint8, bytes32, bytes32).selector 
                                                || f.selector == cancelWithdrawal(uint256).selector
                                                || f.selector == withdraw(uint256).selector 
                                                || f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector
                                                || f.selector == tradeBySourceAmountPermitted(address, address, uint256, uint256, uint256, address, uint8, bytes32, bytes32).selector
                                                || f.selector == tradeByTargetAmount(address, address, uint256, uint256, uint256, address).selector
                                                || f.selector == tradeByTargetAmountPermitted(address, address, uint256, uint256, uint256, address, uint8, bytes32, bytes32).selector 
                                                || f.selector == flashLoan(address, uint256, address, bytes).selector
                                                || f.selector == migrateLiquidity(address, address, uint256, uint256, uint256).selector} {
                                                   
    uint256 status = _status(e);
    require status == 2;

    calldataarg args;
    f@withrevert(e, args);
    assert lastReverted, "Mortal soul cannot get God's power!";
}


// STATUS - in progress
// only users with admin role can call certain functions
// john:
// basic:
rule almightyAdmin(env e, method f) filtered { f -> !f.isView && f.selector != certorafallback_0().selector } {
    bool roleBefore = hasRole(roleAdmin(), e.msg.sender);
    
    calldataarg args;
    f@withrevert(e, args);

    bool isReverted = lastReverted;

    assert  isReverted => (!roleBefore 
                                && f.selector == addPoolCollection(address).selector 
                                    || f.selector == removePoolCollection(address, address).selector 
                                    || f.selector == setLatestPoolCollection(address).selector
                                    || f.selector == createPool(uint16, address).selector 
                                    || f.selector == createPools(uint16, address[]).selector)
    , "With great power comes great responsibility";
}



invariant balanceCorrelationCheck(address PT, address user, env e)
    PoolCol.tokenUserBalance(PT, user) == ptA.balanceOf(e, user)
    filtered { f -> f.selector == deposit(address, uint256).selector || f.selector == createPool(uint16, address).selector || f.selector == tradeBySourceAmount(address, address, uint256, uint256, uint256, address).selector }
    {
        preserved {
            require PT == ptA;
        }
    }
    

// check as above for modifier onlyRoleMember