////////////////////////////////////////////////////
//                   BNTPool                      //
////////////////////////////////////////////////////


// STATUS - in progress 
// Expected to fail because Bancor doesn't have this protection.
// grantRole() also leads to the violation because user could have soemthing before granting them role
invariant noMoneyForAdmin(env e, address user)
    (hasRole(roleBNTPoolTokenManager(), user) || hasRole(roleBNTManager(), user) 
            || hasRole(roleVaultManager(), user) || hasRole(roleFundingManager(), user) 
            || hasRole(DungeonMaster.roleAssetManager(), user))
    => (PoolT.balanceOf(user) == 0 
            && BntGovern.getBNTBalance(e, user) == 0 
            && VbntGovern.getBNTBalance(e, user) == 0)
    {
        preserved with (env e2){
            require user != DungeonMaster;
            require user != _network();
            require user != currentContract;
            require BntGovern._token() != VbntGovern._token();
            // require BntGovern.getToken(e2) != VbntGovern.getToken(e2);
        }
    }







////////////////////////////////////////////////////
//                PendingWithdrawals              //
////////////////////////////////////////////////////

/*
In order to prevent protocol abuse, withdrawal requests are locked for a 
certain (non-zero) period of time.
 *****************
Current status:
# _instate :x
    FAILS because lockDuration is not initialized in constructor.
# _preserved:
    FAILS after calling setLockDuration(uint32) because there is no
    restriction upon the value. 
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


// Attempt to use struct in CVL - IGNORE
rule StructWithdrawalRequest(uint id)
{
    MAIN.WithdrawalRequest var;
    address provider;
    env e;
    sinvoke cancelWithdrawal(e,provider, id);
    require var == MAIN.withdrawalRequest(id) ;
    assert var.provider == 0;
}

// Pool token withdrawal solvency: 
// For a given pool with pool token (poolToken), the sum of all registered pool tokens
// from all requests, must be less or equal to the total supply of that pool token.
//
// Current status : FAILS
// fails for initWithdrawal*
// * see note inside preserved block
// Sasha: now it also fails for completeWithdrawal() because withdrawalRequest cannot be removed because of the bug
// probably better move it to the BancorNetwork

invariant totalRequestPTlessThanSupply(address poolToken)
    sumRequestPoolTokens(poolToken) <= poolTotalSupply(poolToken)
    {
        preserved initWithdrawal(address provider, address poolToken2, uint256 poolTokenAmount) with (env e)
        {
            // In Bancor network, before calling initWithdrawal, the provider transfers its
            // Pool tokens to the _pendingWithdrawal contract, i.e. the protocol.
            require poolToken == poolToken2;
            require poolTokenBalance(poolToken, currentContract) >= poolTokenAmount;
            // If we require invariant of solvency:
            // sum(requests pool tokens) <= sum(user balance) <= Total supply
            // this should probably let the rule pass.
            // sumRequestPoolTokens + poolTokenAmount <= sum(userbalance)   
            require poolTotalSupply(poolToken) >= poolTokenAmount;
        }
    }
   

/// transferred to the BancorNetwork spec
// Once a withdrawal request was registered, it should always
// be possible to cancel it by its provider (without time limitation).
// Current status: PASSES *
// * cancelWithdrawal reverts because safeTransfer call in _cancelWithdrawal reverts.
// One has to make sure that the protocol has enough pool tokens in balance.
// This could be assumed if we are sure that they were given to the protocol in advance.
// _removeWithdrawalRequest may also revert because remove function returns false.
// If one ignores this revert statement, the rule passes.
rule cancellingAlwaysPossible(address provider)
{
    env e;
    address poolToken; 
    address reserveToken = erc20;
    require poolToken == ptA || poolToken == ptB;
    uint256 amount;
    uint id;

    id = initWithdrawal(e, provider, poolToken, amount);
    validRequest(provider, poolToken, reserveToken, amount);
    // No restriction upon the request count can lead to overflow,
    // Here the limit is arbitrary.
    require withdrawalRequestCount(provider) < max_uint;
    ///
    // This requirement is necessary that the transfer of pool tokens
    // back to the provider won't revert.
    require poolTokenBalance(poolToken, currentContract) >= amount;
    // Prevent overflow
    require poolTokenBalance(poolToken, provider) + amount <= max_uint;
    ///
    cancelWithdrawal@withrevert(e, provider, id);

    assert !lastReverted, "cancelWithdrawal reverted for a valid request";
}

/// transferred to the BancorNetwork spec
// A withdrawal request can be registered only if the provider has
// enough pool tokens in the given pool.
// Current status: FAILS*
// *InitWithdrawal is a callee in BancorNetwork, in which the pool tokens are transferred
// from the provider to the protocol.
// Alternatively, we can check that the protocol has enough pool tokens.
// Naturally, the rule would still be violated for the same reason.
rule requestRegisteredForValidProvider(address provider, uint tokenAmount)
{
    env e;
    address poolToken = ptA;
    uint id = initWithdrawal(e,provider,poolToken,tokenAmount);
    //assert ptA.balanceOf(e,provider) >= tokenAmount;
    assert ptA.balanceOf(e,currentContract) >= tokenAmount;
}

/// Should transfer to the BancorNetwork spec:
// The protocol should burn the pool tokens it received from the provider
// after the withdrawal request was completed.
// Current status: ?
rule burnPTsAfterCompleteWithdrawal(address provider, uint PTamount)
{
    env e; env e2;
    bytes32 contextId;
    address poolToken = ptA;
    require provider != currentContract;

    uint id = initWithdrawal(e,provider,poolToken,PTamount);

    uint PTbalance1 = poolTokenBalance(poolToken, currentContract);
    uint totSupply1 = poolTotalSupply(poolToken);

    completeWithdrawal(e2,contextId,provider,id);

    uint PTbalance2 = poolTokenBalance(poolToken, currentContract);
    uint totSupply2 = poolTotalSupply(poolToken);

    assert PTbalance2 + PTamount == PTbalance1 , "Protocol did not remove its pool tokens";
    assert totSupply2 + PTamount == totSupply1 , "The number of burnt PTs is incorrect";
}



// For any provider who completes his/hers withdrawal request,
// his/hers pool token balance must not change.
// Current status : FAILS
// The current implementation of completeWithdrawal transfers PT to the
// provider. We know it should change in the future.
rule ptInvarianceForProvider(uint id)
{
    env e;
    address provider = requestProvider(id);
    bytes32 contID;

    require requestPoolToken(id) == ptA;
    require provider != ptA;
    
    uint PTbalance1 = ptA.balanceOf(e,provider);
        completeWithdrawal(e,contID,provider,id);
    uint PTbalance2 = ptA.balanceOf(e,provider);

    assert PTbalance1 == PTbalance2;
}


// For any registered request, the time it was created must be earlier 
// than the current block time and no earlier than when the request was sent.
// Current status: FAILS
// the createdAt field of the request is given by time() function which supposed
// to give the block.timestamp. For some reason it is not the same as in here.
rule validRequestTime(method f)
{
    env e;
    address provider;
    address poolToken = ptA;
    uint256 amount;
    calldataarg args;

    require e.block.timestamp < max_uint32;
    uint timeInit = e.block.timestamp;
    f(e,args);
    uint id = initWithdrawal(e, provider, poolToken, amount);
    uint32 tmp = _time(e);
    uint256 tmp256 = _time256(e);
    uint time = to_uint256(requestCreatedAt(id));
    uint timeEnd = e.block.timestamp;
    assert timeEnd >= time && time >= timeInit;
}




////////////////////////////////////////////////////
//                PoolCollection                  //
////////////////////////////////////////////////////


/////////////////////////////////////////////////////////////////
//          In progress
//      It fails on WITHDRAW 

rule more_poolTokens_less_TKN(method f)    filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);

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
}


/////////////////////////////////////////////////////////////////
//      Fails
//      but with some unrealistic counter examples

rule tradeChangeExchangeRate(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    bytes32 contextId;
    address sourceToken;
    address targetToken;
    uint256 sourceAmount; require sourceAmount > 0;
    uint256 minReturnAmount = 1;

    uint256 amount1; uint256 amount2;
    uint256 tradingFeeAmount1; uint256 tradingFeeAmount2;
    uint256 networkFeeAmount1; uint256 networkFeeAmount2;

    require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT

    amount1,tradingFeeAmount1,networkFeeAmount1 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    amount2,tradingFeeAmount2,networkFeeAmount2 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    
    require amount1 > 1000;
    // the returned amount from the second trade should be different from the first
    assert amount1 != amount2;
}


// timeout
rule tradeAdditivity(method f) filtered { f -> !f.isView && !f.isFallback }
{
    env e;
        setUp();

    require networkSettings.networkFeePPM() == 0;
    require getPoolDataTradingFee(e,tokenA) == 0;

    storage init = lastStorage;

    bytes32 contextId;
    address sourceToken;
    address targetToken;
    uint256 sourceAmount;
    uint256 minReturnAmount;

    uint256 amount1; uint256 amount2; uint256 amount3;
    uint256 tradingFeeAmount1; uint256 tradingFeeAmount2; uint256 tradingFeeAmount3;
    uint256 networkFeeAmount1; uint256 networkFeeAmount2; uint256 networkFeeAmount3;

    require sourceToken == tokenA || targetToken == tokenA; // the other token is BNT

    amount1,tradingFeeAmount1,networkFeeAmount1 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    amount2,tradingFeeAmount2,networkFeeAmount2 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount, minReturnAmount);
    
    amount3,tradingFeeAmount3,networkFeeAmount3 = tradeBySourceAmount(e,contextId, sourceToken, targetToken, sourceAmount * 2, minReturnAmount) at init;

    assert amount1 + amount2 >= amount3;
}


/////////////////////////////////////////////////////////////////
//      In progress

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
    filtered { f -> !f.isView && !f.isFallback &&
                f.selector != migratePoolIn(address,(address,uint32,bool,bool,(uint32,(uint112,uint112)),uint256,(uint128,uint128,uint256))).selector}
    {
        preserved {
                    require pool == tokenA;
                    setUp();
                  }
        preserved withdraw(bytes32 contextId,address provider,address pool2, uint256 tokenAmount) with (env e1)
                  {
                    require provider == user;
                    require pool2 == tokenA;
                  }

    }


/////////////////////////////////////////////////////////////////
//      Fails.
//      after withdraw all an unlimitted amount of poolTokens might stay in the pool
rule withdrawAll(method f, address provider) filtered { f -> !f.isView && !f.isFallback } 
{
    env e;
        setUp();
    //require e.msg.sender != currentContract && e.msg.sender != _bntPool(e) && e.msg.sender != _masterVault(e);
    require provider !=currentContract && provider !=_bntPool(e) && provider != _masterVault(e);

        bytes32 contextId;
        //address provider = e.msg.sender;
        address pool = tokenA;
        uint256 poolTokenAmount = ptA.totalSupply(e);

    uint256 stakedBalance = getPoolDataStakedBalance(e,pool);
    require stakedBalance == ptA.totalSupply(e);
    setConstants_wmn_only(e,pool); // Insert here function to set parameters to constants.
    
    requireInvariant consistentTradingLiquidity(e , pool);

    uint256 balance1 = tokenA.balanceOf(e,provider);
        uint amount = withdraw(e,contextId,provider,pool,poolTokenAmount);
    uint256 balance2 = tokenA.balanceOf(e,provider);


    assert getPoolDataBntTradingLiquidity(e,pool) == 0 && getPoolDataBaseTokenLiquidity(e,pool) == 0;
}

// Set withdrawal parameters (w,m,n) to constants.
function setConstants_wmn_only(env e, address pool){
    uint256 w = 0;
    uint256 m = 0;//2000;
    uint256 n = 0;//2500;
    address epv = _externalProtectionVault(e);  

    require w == tokenUserBalance(e,pool,epv);
    require m == getPoolDataTradingFee(e,pool);
}


/////////////////////////////////////////////////////////////////
//      Timeout
rule laterWithdrawGreaterWithdraw(method f) filtered { f -> !f.isView && !f.isFallback }
{
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


/////////////////////////////////////////////////////////////////
//      Timeout
//  seems like every rule that calls more than one method timeouts
rule onWithdrawAllGetAtLeastStakedAmount(method f) filtered { f -> !f.isView && !f.isFallback }
{
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

/////////////////////////////////////////////////////////////////
// Time-outs.
// https://vaas-stg.certora.com/output/41958/63355dbc126351e96fa0/?anonymousKey=a0cab2704478832e9814b102c2ecd4cd740b7f05
rule ShareValueUponWithdrawal(method f, address provider, uint share) filtered { f -> !f.isView && !f.isFallback }
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





/////////////////////////////////////////////////////////////////
//      Fails
//      https://vaas-stg.certora.com/output/65782/10e9c2d5beefadc44703/?anonymousKey=885f44fd094a6d88a4a6ef353d601857c631572c

    invariant masterVaultBalanceBaseLiquidity(env e, address pool)
    tokenA.balanceOf(e,_masterVault(e)) == 0 => getPoolDataBaseTokenLiquidity(e,pool) == 0
    {
        preserved
        {
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
            require provider == user;
            require pool2 == tokenA; require pool2 == pool;
            require hasPool(pool2);
        }
        preserved disableTrading(address pool3) with (env e3){
            setUp();
            require pool3 == tokenA; require pool3 == pool;
            require hasPool(pool3);
        }
        preserved enableTrading(address pool4, uint256 bntVirtualBalance, uint256 baseTokenVirtualBalance) with (env e4){
            setUp();
            require pool4 == tokenA; require pool4 == pool;
            require hasPool(pool4);
        }
    }

/////////////////////////////////////////////////////////////////
//      Fails
//      https://vaas-stg.certora.com/output/65782/9ebfa7176e83f22e70e3/?anonymousKey=8cd44f516be267bac8202d0b7960726bc7137458

    invariant stakedBalanceMasterVaultBalance(env e, address pool)
    tokenA.balanceOf(e,_masterVault(e)) == 0 => getPoolDataStakedBalance(e,pool) == 0 
    {
        preserved{
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
            require provider == user;
            require pool2 == tokenA; require pool2 == pool;
            require hasPool(pool2);
        }
        preserved disableTrading(address pool3) with (env e3){
            setUp();
            require pool3 == tokenA; require pool3 == pool;
            require hasPool(pool3);
        }
        preserved enableTrading(address pool4, uint256 bntVirtualBalance, uint256 baseTokenVirtualBalance) with (env e4){
            setUp();
            require pool4 == tokenA; require pool4 == pool;
            require hasPool(pool4);
        }
    }


rule stableRateAfterTrade(uint amount)
{
    env e;
    bytes32 contextId;
    address targetToken;
    address sourceToken;

    require sourceToken == tokenA || targetToken == tokenA;
    require amount > 0;
    require getPoolDataBntTradingLiquidity(e,tokenA) > 0;
    require getPoolDataBaseTokenLiquidity(e,tokenA) > 0;
    require isPoolStable(e,tokenA);

        tradeBySourceAmount(e,contextId, sourceToken, targetToken, amount, 1);

    assert !isPoolUnstable(e,tokenA);
}

rule stableRateAfterTradeRealistic(uint amount)
{
    env e;
    bytes32 contextId;
    address targetToken;
    address sourceToken;
    uint256 tradeFee = getPoolDataTradingFee(e,tokenA);
    uint256 networkFee = networkSettings.networkFeePPM();

    require sourceToken == tokenA || targetToken == tokenA;
    require amount > 0;
    require getPoolDataBntTradingLiquidity(e,tokenA) >= 1000000000;
    require getPoolDataBaseTokenLiquidity(e,tokenA) >= 1000000000;
    require getPoolDataAverageRateD(e,tokenA) >= 0;
    require getPoolDataAverageRateN(e,tokenA) >= 0;
    require tradeFee  == 0;
    require networkFee == 0;

    require isPoolStable(e,tokenA);
        tradeByTargetAmount(e,contextId, sourceToken, targetToken, amount, max_uint);

    assert !isPoolUnstable(e,tokenA);
}




////////////////////////////////////////////////////
//                 BancorNetwork                  //
////////////////////////////////////////////////////

//       Invariants

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








// STATUS - in progress (reachability fail)
// Pool tokens must be burnt after withdrawal.
// https://vaas-stg.certora.com/output/3106/38d2146dde7df24aa49a/?anonymousKey=6b43adb61a5073ec23c32430d0624e1a5cf1597a
rule mustBeBurned(env e) {
    uint256 id;
    address poolToken; uint256 ptToBeBurned; uint256 originalPTAmount;
    bytes32 contextId;

    require contextId == _withdrawContextId(e, id, e.msg.sender);
    require e.msg.sender != currentContract;

    uint256 ptBalanceBefore = ptA.balanceOf(e, currentContract);  

    storage initialStorage = lastStorage;
    
    poolToken, ptToBeBurned, originalPTAmount = PendWit.completeWithdrawal(e, contextId, e.msg.sender, id);
    
    require poolToken != _bntPoolToken(e);
    
    withdraw(e, id) at initialStorage;

    uint256 ptBalanceAfter = ptA.balanceOf(e, currentContract);

    assert ptBalanceBefore == ptBalanceAfter + ptToBeBurned;
}


