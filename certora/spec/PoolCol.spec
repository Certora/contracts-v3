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
    networkSettings.minLiquidityForTrading() returns(uint256)
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

    callRemoveTokenFromWhiteList(address) envfree
    // safeTransferFrom(address, address, uint256) envfree
}
 
function setUp() {
    require poolToken(tokenA) == ptA;
    require poolToken(tokenB) == ptB;
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
    require w == tokenUserBalance(env1, pool, epv);
    require m == getPoolDataTradingFee(env1, pool);
    require n == networkSettings.withdrawalFeePPM(env1);
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
    require w == tokenUserBalance(env1, pool, epv);
    require m == getPoolDataTradingFee(env1, pool);
    require n == networkSettings.withdrawalFeePPM(env1);
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
    require w == tokenUserBalance(env1, pool, epv);
    require m == getPoolDataTradingFee(env1, pool);
    require n == networkSettings.withdrawalFeePPM(env1);
}

// Set withdrawal parameters (w,m,n) to constants.
function setConstants_wmn_only(env env1, address pool){
    uint256 w = 0;
    uint256 m = 2000;
    uint256 n = 2500;
    address epv = _externalProtectionVault(env1);  

    require w == tokenUserBalance(env1, pool, epv);
    require m == getPoolDataTradingFee(env1, pool);
    require n == networkSettings.withdrawalFeePPM(env1);
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

function callFuncWithParams(method f, env e, address pool) {
bool flag;
uint256 x;
bytes32 contextId;
address poolCollection;
address sourceToken;
address targetToken;
uint256 sourceAmount;
uint256 minReturnAmount;
uint256 maxSourceAmount;
address provider;
uint256 tokenAmount;

    if (f.selector == enableDepositing(address,bool).selector ) {
        enableDepositing(e, pool, flag);
    }

    else if (f.selector == migratePoolOut(address,address).selector ) {
        migratePoolOut(e, pool, poolCollection);
    }
/*else if (f.selector == tradeInputAndFeeByTargetAmount(address,address,uint256).selector) {
}*/
    else if (f.selector == enableTrading(address,uint256,uint256).selector) {
        uint256 bntVirtualBalance;
        uint256 baseTokenVirtualBalance;
        enableTrading(e, pool, bntVirtualBalance, baseTokenVirtualBalance);
    }
    else if (f.selector == tradeByTargetAmount(bytes32,address,address,uint256,uint256).selector){
        tradeByTargetAmount(e,contextId, sourceToken, targetToken, tokenAmount, maxSourceAmount);
    } 
    else if (f.selector == tradeBySourceAmount(bytes32,address,address,uint256,uint256).selector){
        tradeBySourceAmount(e,contextId, sourceToken, targetToken, tokenAmount, minReturnAmount);
    }
    else if (f.selector == depositFor(bytes32,address,address,uint256).selector){
        depositFor(e, contextId, provider, pool, tokenAmount);
    }
/* else if (f.selector == tradeOutputAndFeeBySourceAmount(address,address,uint256).selector){

} */
    else if (f.selector == disableTrading(address).selector){
        disableTrading(e, pool);
    }
    else if (f.selector == withdraw(bytes32,address,address,uint256).selector){
        withdraw(e, contextId, provider, pool, tokenAmount);
    }
    else {
        calldataarg args;
        f(e,args);
    }
}

// rule sanity(method f)
// {
// 	env e;
// 	calldataarg args;
// 	santasLittleHelper(f, e);
// 	assert false;
// }

rule more_poolTokens_less_TKN(method f){
    env e;
        setUp();

    require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);
    // calldataarg args;

    uint256 tkn_balance1 = tokenA.balanceOf(e,e.msg.sender);
    uint256 poolToken_balance1 = ptA.balanceOf(e,e.msg.sender);

        bytes32 contextId;
        address provider = e.msg.sender;
        address pool = tokenA;
        uint256 tokenAmount;

    if(f.selector == depositFor(bytes32,address,address,uint256).selector){

        uint256 amount = depositFor(e,contextId,provider,pool,tokenAmount);        
    }
    else
    if(f.selector == withdraw(bytes32, address, address, uint256).selector){        
        withdraw(e,contextId, provider, pool, tokenAmount);
    }
    else
    callFuncWithParams(f, e, pool);
    // f(e,args);

    uint256 tkn_balance2 = tokenA.balanceOf(e,e.msg.sender);
    uint256 poolToken_balance2 = ptA.balanceOf(e,e.msg.sender);

    assert tkn_balance2 > tkn_balance1 <=> poolToken_balance2 < poolToken_balance1;
    assert tkn_balance2 < tkn_balance1 <=> poolToken_balance2 > poolToken_balance1;
    // assert tokenAmount > 0 => amount > 0;
}

rule tradeChangeExchangeRate(){
    env e;
        setUp();

    bytes32 contextId;
    address sourceToken;
    address targetToken;
    uint256 sourceAmount;
    uint256 minReturnAmount;

    uint256 amount1; uint256 amount2;
    uint256 tradingFeeAmount1; uint256 tradingFeeAmount2;
    uint256 networkFeeAmount1; uint256 networkFeeAmount2;

    require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT

    amount1,tradingFeeAmount1,networkFeeAmount1 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    amount2,tradingFeeAmount2,networkFeeAmount2 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    
    // the returned amount from the second trade should be different from the first
    assert amount1 != amount2;
}

invariant tradingEnabledImplLiquidity(address pool, env e)
    getPoolDataTradingEnabled(e,pool) => 
                                        //  getPoolDataBaseTokenLiquidity(e,pool) > 0 
                                        //  &&
                                        //  getPoolDataBntTradingLiquidity(e,pool) > 0 
                                        //  &&
                                         getPoolDataStakedBalance(e,pool) > 0
                                        //  &&
                                        //  getPoolTokenTotalSupply(e,poolToken(pool)) > 0
                                        //  &&
                                        //  isPoolValid(e,pool)
    filtered { f -> !f.isView &&
                f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112)),uint256,(uint128,uint128,uint256))).selector}
    {
        preserved {
                    require pool == tokenA;
                    require networkSettings.minLiquidityForTrading(e) > 0;

                  }
        preserved withdraw(bytes32 contextId,address provider,address pool2, uint256 tokenAmount) with (env e1)
                  {
                    require provider == user;
                    require pool2 == tokenA;
                  }

    }

rule tradeAllBntTokensShouldFail(){
    env e;
        setUp();

    require networkSettings.minLiquidityForTrading(e) > 0;

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
rule tradeWhenZeroTokensFail(){
    env e;
        setUp();

    require networkSettings.minLiquidityForTrading(e) > 0;

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

rule tradeWhenZeroLiquidity(){
    env e;
        // setUp();

    bytes32 contextId;
    address sourceToken;
    address targetToken;
    uint256 targetAmount;// = getPoolDataBaseTokenLiquidity(e,targetToken);
    uint256 maxSourceAmount;

    uint256 amount;
    uint256 tradingFeeAmount;
    uint256 networkFeeAmount;

    require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT
    require networkSettings.minLiquidityForTrading(e) == 0;
    require getPoolDataBntTradingLiquidity(e,tokenA) == 0;

    amount,tradingFeeAmount,networkFeeAmount = tradeByTargetAmount@withrevert(e,contextId, sourceToken, targetToken, targetAmount, maxSourceAmount);

    assert lastReverted;
}

rule withdrawAll(address provider){
    env e;
    //require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);
    require provider !=currentContract && provider !=_bntPool(e) && provider != _masterVault(e);

        bytes32 contextId;
        //address provider = e.msg.sender;
        address pool = tokenA;
        require ptA == poolToken(pool);
        uint256 poolTokenAmount = ptA.totalSupply(e);

            require networkSettings.minLiquidityForTrading(e) > 0;

    uint256 stakedBalance = getPoolDataStakedBalance(e,pool);
    // setConstants_wmn_only(e,pool); // Insert here function to set parameters to constants.
    uint256 balance1 = tokenA.balanceOf(e,provider);
        uint amount = withdraw(e,contextId,provider,pool,poolTokenAmount);
    uint256 balance2 = tokenA.balanceOf(e,provider);


    assert balance2 - balance1 == stakedBalance ;    
    assert !getPoolDataTradingEnabled(e,pool); 
    //assert false;
}

rule laterWithdrawGreaterWithdraw(){
    env e1;env e2;

    storage init = lastStorage;

    address provider = e1.msg.sender;
    require provider !=currentContract && provider !=_bntPool(e1) && provider != _masterVault(e1);

    bytes32 contextId;
    address pool = tokenA;
    uint256 poolTokenAmount;

        uint amount1 = withdraw(e1,contextId,provider,pool,poolTokenAmount);
        uint amount2 = withdraw(e2,contextId,provider,pool,poolTokenAmount) at init;

    assert e2.block.timestamp > e1.block.timestamp => amount1 >= amount2;

}


rule onWithdrawAllGetAtLeastStakedAmount(){
    env e;
        setUp();
    require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);


        bytes32 contextId;
        address provider;
        address pool = tokenA;
        uint256 tokenAmount;

    uint poolTokenAmount = depositFor(e,contextId,provider,pool,tokenAmount);
    uint amount = withdraw(e,contextId,provider,pool,poolTokenAmount);

    assert amount >= tokenAmount;// * 9975 / 10000;
}

// Time-outs.
// https://vaas-stg.certora.com/output/41958/63355dbc126351e96fa0/?anonymousKey=a0cab2704478832e9814b102c2ecd4cd740b7f05
rule invariantShareValueUponWithdrawal(address provider, uint share)
{
    env e;
    address pool = tokenA;
    address pool2;
    address PT = ptA;
    address PT2 = ptB;
    bytes32 contextId;
    uint ptAmount;

    require pool2 == tokenA || pool2 == tokenB;
    require pool != pool2 => poolToken(pool2) == PT2;
    require poolToken(pool) == PT;
    
    uint totSupply = getPoolTokenTotalSupply(e,poolToken(pool2));

    uint usersValue1 = poolTokenToUnderlying(e,pool,share);
        setConstants_wmn_only(e,pool2);
        withdraw(e,contextId,provider,pool2,ptAmount);
    uint usersValue2 = poolTokenToUnderlying(e,pool,share);

    assert usersValue1 != usersValue2 => ptAmount == totSupply && usersValue2 == 0,
        "A withdrawal changed the share value in the pool";
}
    

invariant differentTokens(address tknA, address tknB)
    hasPool(tknA) && hasPool(tknB) && tknA != tknB => poolToken(tknA) != poolToken(tknB)
    filtered { f -> !f.isView &&
                f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112)),uint256,(uint128,uint128,uint256))).selector &&
                f.selector != migratePoolOut(address,address).selector
            }
    {
       preserved withdraw(bytes32 contextId,address provider,address pool, uint256 tokenAmount) with (env e)
       {
           require provider == user;
       }
    }


    invariant zeroPoolTokensZeroStakedBalance(address pool, env e)
        getPoolTokenTotalSupply(e,poolToken(pool))== 0 <=> getPoolDataStakedBalance(e,pool) == 0
    {
        preserved {
            require pool == tokenA;
            require hasPool(pool);
        }
    }

    invariant consistentTradingLiquidity(env e,address pool)
        getPoolDataBntTradingLiquidity(e,pool) ==0 <=> getPoolDataBaseTokenLiquidity(e,pool) ==0
    {
        preserved
        {
            require getPoolDataTradingFee(e, pool) <= 10000;
            require pool == tokenA;
            require hasPool(pool);
        }
    }

invariant stakedBalanceMasterVaultBalance(env e)
    tokenA.balanceOf(e,_masterVault(e)) ==0 => getPoolDataStakedBalance(e,tokenA) ==0 
    // {
    //     preserved{
    //         require poolToken(tokenA) == ptA;
    //         address pool;
    //         require pool !=0 && pool !=_masterVault(e);
    //         require (pool != tokenA =>  getPoolDataStakedBalance(e,pool)==0);
    //     }
    // }

    invariant zeroStakedBalanceZeroLiquidity(env e, address pool)
        getPoolDataStakedBalance(e,pool) == 0 => getPoolDataBntTradingLiquidity(e,pool) ==0
    filtered { f -> !f.isView &&
                f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112)),uint256,(uint128,uint128,uint256))).selector}
    {
        preserved {
                    require pool == tokenA;
                    require networkSettings.minLiquidityForTrading(e) > 0;

                  }
        preserved withdraw(bytes32 contextId,address provider,address pool2, uint256 tokenAmount) with (env e1)
                  {
                    require provider == user;
                    require pool2 == tokenA;
                  }

    }

    rule withdrawWhenBntIsZero(){
    env e;


    address provider = e.msg.sender;
    require provider !=currentContract && provider !=_bntPool(e) && provider != _masterVault(e);

    bytes32 contextId;
    address pool = tokenA;
    uint256 poolTokenAmount;

        // require ptA == poolToken(pool);
        // require ptA.balanceOf(e,provider) == ptA.totalSupply(e); // assume one LP

    require getPoolDataBntTradingLiquidity(e,pool) ==0;
        uint amount = withdraw@withrevert(e,contextId,provider,pool,poolTokenAmount);

    assert !lastReverted => amount == 0;

}


/*
invariant isWhiteListed(address token, env e)
    hasPool(token) => isTokenWhitelisted(e,token)
*/
    
// rule poolTokenValueMonotonic(){
//     env e1; env e2;

//     uint poolTokenValue = 

// }