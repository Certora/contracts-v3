import "../helpers/erc20.spec"

using DummyERC20A as tokenA
using DummyERC20B as tokenB
using DummyPoolTokenA as ptA
using DummyPoolTokenB as ptB
using Receiver1 as user
using NetworkSettings as networkSettings
using ExternalProtectionVault as EPV

methods {
    renounceFunding(bytes32, address, uint256) => DISPATCHER(true)
    // requestFunding(bytes32, address, uint256) => DISPATCHER(true)
    // availableFunding(address) returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns (uint32) => DISPATCHER(true)
    
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkSettings.minLiquidityForTrading() returns(uint256) envfree
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    acceptOwnership() => DISPATCHER(true)
    withdrawFunds(address, address, uint256) => DISPATCHER(true)   
    isTokenWhitelisted(address) returns(bool) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    createPoolToken(address) returns(address) => DISPATCHER(true) //NONDET       // caused issues
    // latestPoolCollection(uint16) returns(address) => DISPATCHER(true) lets have it nondet
    issue(address, uint256) => DISPATCHER(true)
    transferOwnership(address) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    // receive() => DISPATCHER(true)
    sendTo() returns(bool) => DISPATCHER(true)
    poolToken(address) returns(address) envfree
    hasPool(address) returns (bool) envfree
    _bnt() returns (address) envfree
    migratePoolOut(address, address)
    //mulDivF(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDivIfWithRemainder(x,y,z)
    //mulDivC(uint256 x, uint256 y, uint256 z) returns (uint256) => simpleMulDivIfWithRemainder(x,y,z)
    //callRemoveTokenFromWhiteList(address) envfree
    // safeTransferFrom(address, address, uint256) envfree
}
        
 
function setUp() {
    require poolToken(tokenA) == ptA;
    require poolToken(tokenB) == ptB;
    require networkSettings.minLiquidityForTrading() > 0;
}


// Summary for mulDivF:
// quotient y/z is either 0,1,2,3,10 or 1/2, 1/3, 1/10.
// Nothing resticts the value of x/z;
function simpleMulDivIf(uint256 x, uint256 y, uint256 z) returns uint256 
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
    else if (y == 10 * z)     {f = 10 * x;}
    else if (x == 10 * z)     {f = 10 * y;}
    else if (10 * y == z )  {f = x / 10;}
    else if (10 * x == z )  {f = y / 10;}
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


// `depositFor` should return positive number after successful call.
// rule afterDepositAmountGzero(method f)    filtered { f -> !f.isView && !f.isFallback }
// {
//     env e;
//     setUp();

//     require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);

//     bytes32 contextId;
//     address provider = e.msg.sender;
//     address pool = tokenA;
//     uint256 tokenAmount;

//     uint256 amount = depositFor(e, contextId, provider, pool, tokenAmount);   

//     assert amount > 0;
// }


// It should be imposssible to trade all BNT tokens at once.
// rule tradeAllBntTokensShouldFail(method f) filtered { f -> !f.isView && !f.isFallback }
// {
//     env e;
//     setUp();

//     bytes32 contextId;
//     address sourceToken = tokenA;
//     address targetToken;// = tokenB;
//     uint256 targetAmount = getPoolDataBntTradingLiquidity(e,sourceToken);
//     uint256 maxSourceAmount;// = 2^255;

//     uint256 amount;
//     uint256 tradingFeeAmount;
//     uint256 networkFeeAmount;

//     amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

//     assert  lastReverted;
// }


// It should be imposssible to trade if BNT or TKN trading liquidity is 0.
// rule tradeWhenZeroTokensRevert(method f) filtered { f -> !f.isView && !f.isFallback }
// {
//     env e;
//     setUp();

//     bytes32 contextId;
//     address sourceToken = tokenA;
//     address targetToken;// = tokenB;
//     uint256 targetAmount;
//     uint256 maxSourceAmount;

//     uint256 amount;
//     uint256 tradingFeeAmount;
//     uint256 networkFeeAmount;

//     require getPoolDataBntTradingLiquidity(e,sourceToken) == 0 || getPoolDataBaseTokenLiquidity(e,sourceToken) == 0;

//     amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

//     assert  lastReverted;
// }


// It should be imposssible to trade if BNT trading liquidity and `minLiquidityForTrading` is 0.
// rule tradeWhenZeroLiquidity(method f) filtered { f -> !f.isView && !f.isFallback }
// {
//     env e;

//     bytes32 contextId;
//     address sourceToken;
//     address targetToken;
//     uint256 targetAmount;
//     uint256 maxSourceAmount;

//     uint256 amount;
//     uint256 tradingFeeAmount;
//     uint256 networkFeeAmount;

//     require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT
//     require networkSettings.minLiquidityForTrading() == 0;
//     require getPoolDataBntTradingLiquidity(e, tokenA) == 0;

//     amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

//     assert lastReverted;
// }


// violations, timeouts, reachability failed for createPool() (run on --staging) https://vaas-stg.certora.com/output/3106/ea6ec3fd9bffa617257a/?anonymousKey=371ca6a4fb85148864d34d5d95b1e07a00ccad27
// Average rate always remains positive.
invariant rateIsPositive(env e, address pool)
    averageRateIsPositive(e, pool)
        {
            preserved{
                setUp();
                require pool == tokenA;
                require hasPool(pool);
            }
        }


// reachability failed for createPool() (run on --staging), out of memory fails (probably need to add the flag for short output) 
// https://vaas-stg.certora.com/output/3106/9b6692fe429340779fe5/?anonymousKey=f7f824a128c2e18bd56c9fb01686dfad28dc6835 
// Average rate cannot be 0.
rule averageRateNonZero(env e, method f, address pool) filtered { f -> !f.isView && !f.isFallback &&
                f.selector != migratePoolOut(address, address).selector}
{
    calldataarg args;
    setUp();
    require pool == tokenA;
    require hasPool(pool);

    require getPoolDataAverageRateD(e,pool) != 0;

    f(e,args);

    assert getPoolDataAverageRateD(e,pool) != 0;
}


// reachability failed for createPool() (run on --staging): https://vaas-stg.certora.com/output/3106/b6212683ea8a697ee78a/?anonymousKey=fd56a6e3a7cd75f2531527a817bc88cd257bb8fe
// Different pools have different pool tokens.
invariant differentTokens(address tknA, address tknB)
    hasPool(tknA) && hasPool(tknB) && tknA != tknB => poolToken(tknA) != poolToken(tknB)
    filtered { f -> !f.isView 
                        && !f.isFallback 
                        && f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112),(uint112,uint112)),(uint128,uint128,uint256))).selector
    }
    {
       preserved{
            setUp();
            require tknA == tokenA;
            require tknB == tokenB;
            requireInvariant notHasPoolNotHasPoolToken(tknA);
       }
       preserved withdraw(bytes32 contextId,address provider,address pool, uint256 poolTokenAmount, uint256 baseTokenAmount) with (env e)
       {
            setUp();
            require provider == user;
            require tknA == tokenA;
            require tknB == tokenB;
            require pool == tknA || pool == tknB;
            require hasPool(pool);
       }
    }


// reachability failed for createPool() (run on --staging) - https://vaas-stg.certora.com/output/3106/09d94ffe92fdb87c7305/?anonymousKey=db4475fb21b0f84a4720ce05f4b1d79e88d99a34
// assuming that if pool doesn't exist in `_pools`, `poolToken` is equal to 0
invariant notHasPoolNotHasPoolToken(address pool)
    !hasPool(pool) => poolToken(pool) == 0
    {
       preserved{
            setUp();
            require pool == tokenA;
       }
    }


// reachability failed for createPool() and two violations in trades (run on --cloud) - https://prover.certora.com/output/3106/a835072ad8324beeea5c/?anonymousKey=dfbc3151581f6073a4aeafe744517bf2b47e3887
// it's strange but it seems like on cloud we don't have 2h run limit but have it on staging. so on cloud no 2h hard stop (run takes 2h40mins), on staging 2h hard stop
// If staked balance is zero, then pool token balance is zero too.
invariant zeroPoolTokensZeroStakedBalance(address pool, env e)
    getPoolDataStakedBalance(e,pool) == 0 => getPoolTokenTotalSupply(e,poolToken(pool))== 0
    {
        preserved {
            setUp();
            require pool == tokenA;
            require hasPool(pool);
        }
        preserved depositFor(bytes32 contextId,address provider, address pool1, uint256 tokenAmount) with (env e1){
            setUp();
            require pool1 == tokenA; require pool1 == pool;
            require hasPool(pool1);
        }
        preserved withdraw(bytes32 contextId,address provider,address pool2, uint256 poolTokenAmount, uint256 baseTokenAmount) with (env e2)
        {
            setUp();
            require pool2 == tokenA; require pool2 == pool;
            require hasPool(pool2);
            require provider == user;
        }
    }


// reachability failed for createPool() and two violations in trades (run on --cloud) - https://prover.certora.com/output/3106/bb78c0bbc628f9fa74f2/?anonymousKey=80975525418784b450c6b298fb6ddd6deccad108
// the same issue as above but here mostly everything has results (run on --staging): https://vaas-stg.certora.com/output/3106/c2e20e3206787b6cfa29/?anonymousKey=894281161b2d153aabc156285dce583c827da482
// If BNT trading liquidity is zero, then TKN trading liquidity is zero too and vice versa.
invariant consistentTradingLiquidity(env e,address pool)
    getPoolDataBntTradingLiquidity(e,pool) == 0 <=> getPoolDataBaseTokenLiquidity(e,pool) == 0
    {
        preserved
        {
            setUp();
            require pool == tokenA;
            require hasPool(pool);
        }
    }



// violation (run on --staging jtoman/bancor-opt) https://vaas-stg.certora.com/output/3106/1d8a9fb71c0161128f5a/?anonymousKey=bcd6f6f15d748587cf2489ca0af9a87f1991f175
// If BNT trading liquidity is 0, then we cannot withdraw anything.
rule withdrawWhenBntIsZero(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;

    address provider = e.msg.sender;
    require provider !=currentContract && provider !=_bntPool(e) && provider != _masterVault(e);

    bytes32 contextId;
    address pool = tokenA;
    uint256 poolTokenAmount; uint256 baseTokenAmount;

    require getPoolDataBntTradingLiquidity(e,pool) == 0;
    uint amount = withdraw@withrevert(e, contextId, provider, pool, poolTokenAmount, baseTokenAmount);

    assert !lastReverted => amount == 0;
}
