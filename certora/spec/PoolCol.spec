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
    networkSettings.networkFeePPM()  returns(uint32) envfree
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

function constQuotient(uint256 x, uint256 y, uint256 z, uint256 q, uint256 f) 
        returns bool {
            return ( x == q * z && f == q * y ) || 
                    ( q * x == z && f == y / q && y % q ==0 ) ||
                    ( y == q * z && f == q * x ) || 
                    ( q * y == z && f == x / q && x % q ==0);
        }
        

// Allowing division remainders
function constQuotientWithRemainder(uint256 x, uint256 y, uint256 z, uint256 q, uint256 f) 
        returns bool {
            return 
            ( x == q * z && f == q * y ) || 
            ( q * x == z && f == y / q ) ||
            ( y == q * z && f == q * x ) || 
            ( q * y == z && f == x / q );
        } 
        
 
function setUp() {
    require poolToken(tokenA) == ptA;
    require poolToken(tokenB) == ptB;
    require networkSettings.minLiquidityForTrading() > 0;
    require networkSettings.networkFeePPM() <= 1000000;
}

// Set all withdrawal parameters, but (x,e), to constants (deficit)
function setConstants_x_e(env env1, address pool){

    uint256 a = 291762234165599000000000;
    uint256 b = 216553090379207000000;
    uint256 c = 21681452129588000000;
    uint256 w = 0;
    uint256 m = 0;//2000;
    uint256 n = 0;//2500;
    address epv = _externalProtectionVault(env1);

    require a == getPoolDataBntTradingLiquidity(env1,pool);
    require b == getPoolDataBaseTokenLiquidity(env1,pool);
    require c == tokenUserBalance(env1,pool,_masterVault(env1)) - 
                getPoolDataBaseTokenLiquidity(env1,pool);
    //require e == getPoolDataStakedBalance(env1,pool);
    require w == tokenUserBalance(env1,pool,epv);
    require m == getPoolDataTradingFee(env1,pool);
    require n == networkSettings.networkFeePPM();
}

// Set all withdrawal parameters, but (x,a), to constants (deficit)
function setConstants_x_a(env env1, address pool){

    uint256 e = 239020803918874000000;
    uint256 b = 216553090379207000000;
    uint256 c = 21681452129588000000;
    uint256 w = 0;
    uint256 m = 2000;
    uint256 n = 2500;
    address epv = _externalProtectionVault(env1); 

    //require a == getPoolDataBntTradingLiquidity(env1,pool);
    require b == getPoolDataBaseTokenLiquidity(env1,pool);
    require c == tokenUserBalance(env1,pool,_masterVault(env1)) - 
                getPoolDataBaseTokenLiquidity(env1,pool);
    require e == getPoolDataStakedBalance(env1,pool);
    require w == tokenUserBalance(env1,pool,epv);
    require m == getPoolDataTradingFee(env1,pool);
    require n == networkSettings.networkFeePPM();
}

// Set all withdrawal parameters, but x, to constants (deficit)
function setConstants_x(env env1, address pool){

    uint256 a = 291762234165599000000000;
    uint256 b = 216553090379207000000;
    uint256 c = 21681452129588000000;
    uint256 e = 239020803918874000000;
    uint256 w = 0;
    uint256 m = 2000;
    uint256 n = 2500;
    address epv = _externalProtectionVault(env1);  

    require a == getPoolDataBntTradingLiquidity(env1,pool);
    require b == getPoolDataBaseTokenLiquidity(env1,pool);
    require c == tokenUserBalance(env1,pool,_masterVault(env1)) - 
                getPoolDataBaseTokenLiquidity(env1,pool);
    require e == getPoolDataStakedBalance(env1,pool);
    require w == tokenUserBalance(env1,pool,epv);
    require m == getPoolDataTradingFee(env1,pool);
    require n == networkSettings.networkFeePPM();
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

// Set withdrawal parameters (w,m,n) to constants.
function setConstants_wmn_only(env e, address pool){
    uint256 w = 0;
    uint256 m = 0;//2000;
    uint256 n = 0;//2500;
    address epv = _externalProtectionVault(e);  

    require w == tokenUserBalance(e,pool,epv);
    require m == getPoolDataTradingFee(e,pool);
    require n == networkSettings.networkFeePPM();
}

function santasLittleHelper(method f, env e){
    if (f.selector == migratePoolOut(address, address).selector) {
        address pool; address targetPoolCollection;
        require pool == tokenA || pool == tokenB;
        require poolToken(pool) == ptA || poolToken(pool) == ptB;
		migratePoolOut(e, pool, targetPoolCollection);
	} else {
        calldataarg args;
        f(e, args);
    }
}


// `depositFor` should return positive number after successful call.
rule afterDepositAmountGzero(method f)    filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);

        bytes32 contextId;
        address provider = e.msg.sender;
        address pool = tokenA;
        uint256 tokenAmount;

        uint256 amount = depositFor(e, contextId, provider, pool, tokenAmount);   

    assert amount > 0;
}


// It should be imposssible to trade all BNT tokens at once.
rule tradeAllBntTokensShouldFail(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    bytes32 contextId;
    address sourceToken = tokenA;
    address targetToken;// = tokenB;
    uint256 targetAmount = getPoolDataBntTradingLiquidity(e,sourceToken);
    uint256 maxSourceAmount;// = 2^255;

    uint256 amount;
    uint256 tradingFeeAmount;
    uint256 networkFeeAmount;

    amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

    assert  lastReverted;
}


// It should be imposssible to trade if BNT or TKN trading liquidity is 0.
rule tradeWhenZeroTokensRevert(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    bytes32 contextId;
    address sourceToken = tokenA;
    address targetToken;// = tokenB;
    uint256 targetAmount;
    uint256 maxSourceAmount;

    uint256 amount;
    uint256 tradingFeeAmount;
    uint256 networkFeeAmount;

    require getPoolDataBntTradingLiquidity(e,sourceToken) == 0 || getPoolDataBaseTokenLiquidity(e,sourceToken) == 0;

    amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

    assert  lastReverted;
}


// It should be imposssible to trade if BNT trading liquidity and `minLiquidityForTrading` is 0.
rule tradeWhenZeroLiquidity(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;

    bytes32 contextId;
    address sourceToken;
    address targetToken;
    uint256 targetAmount;
    uint256 maxSourceAmount;

    uint256 amount;
    uint256 tradingFeeAmount;
    uint256 networkFeeAmount;

    require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT
    require networkSettings.minLiquidityForTrading() == 0;
    require getPoolDataBntTradingLiquidity(e, tokenA) == 0;

    amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

    assert lastReverted;
}


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


// Different pools have different pool tokens.
invariant differentTokens(address tknA, address tknB)
    hasPool(tknA) && hasPool(tknB) && tknA != tknB => poolToken(tknA) != poolToken(tknB)
    filtered { f -> !f.isView && !f.isFallback &&
                f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112)),uint256,(uint128,uint128,uint256))).selector
            }
    {
       preserved{
            setUp();
            require tknA == tokenA;
            require tknB == tokenB;
            requireInvariant notHasPoolNotHasPoolToken(tknA);
       }
       preserved withdraw(bytes32 contextId,address provider,address pool, uint256 tokenAmount) with (env e)
       {
            setUp();
            require provider == user;
            require tknA == tokenA;
            require tknB == tokenB;
            require pool == tknA || pool == tknB;
            require hasPool(pool);
       }
    }

invariant notHasPoolNotHasPoolToken(address pool)
    !hasPool(pool) => poolToken(pool) == 0
    {
       preserved{
            setUp();
            require pool == tokenA;
       }
    }


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
        preserved withdraw(bytes32 contextId,address provider,address pool2, uint256 tokenAmount) with (env e2)
        {
            setUp();
            require pool2 == tokenA; require pool2 == pool;
            require hasPool(pool2);
            require provider == user;
        }
    }


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


// `networkFeePPM` cannot exceed 1000000.
invariant networkFeePPM()
    networkSettings.networkFeePPM() <= 1000000


// If BNT trading liquidity is 0, then we cannot withdraw anything.
rule withdrawWhenBntIsZero(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;

    address provider = e.msg.sender;
    require provider !=currentContract && provider !=_bntPool(e) && provider != _masterVault(e);

    bytes32 contextId;
    address pool = tokenA;
    uint256 poolTokenAmount;

    require getPoolDataBntTradingLiquidity(e,pool) == 0;
        uint amount = withdraw@withrevert(e,contextId,provider,pool,poolTokenAmount);

    assert !lastReverted => amount == 0;
}
