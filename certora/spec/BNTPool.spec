import "../helpers/erc20.spec"

using DummyERC20bnt as DummyBNT
using DummyTokenGovernanceA as BntGovern
using DummyTokenGovernanceB as VbntGovern
using PoolToken as PoolT
using MasterVault as DungeonMaster
using TestUpgradeable as Upgrade
using NetworkSettings as NetSet

methods {
    networkFeePPM() returns(uint32) envfree => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    isTokenWhitelisted(address) returns(bool) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    acceptOwnership() envfree => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    issue(address, uint256) => DISPATCHER(true)

    PoolT.balanceOf(address) returns(uint256) envfree
    PoolT.totalSupply() returns(uint256) envfree

    // Upgrade.
    hasRole(bytes32, address) returns(bool) envfree

    DungeonMaster.roleAssetManager() returns(bytes32) envfree

    NetSet.poolFundingLimit(address) returns(uint256) envfree

    BntGovern._token() returns(address) envfree
    VbntGovern._token() returns(address) envfree

    _poolToken() returns(address) envfree
    
    _bnt() returns(address) envfree
    _bntGovernance() returns(address) envfree
    _vbntGovernance() returns(address) envfree
    _network() returns(address) envfree

    onFeesCollected(address, uint256, bool)
    withdraw(bytes32, address, uint256) returns(uint256)
    withdrawFunds(address, address, uint256)
    depositFor(bytes32, address, uint256, bool, uint256) returns(uint256)
    requestFunding(bytes32, address, uint256)
    renounceFunding(bytes32, address, uint256)
    grantRole(bytes32, address)
    mint(address, uint256)
    burnFromVault(uint256)

    stakedBalance() returns(uint256) envfree
    withdrawalAmount(uint256) returns(uint256) envfree
    roleBNTPoolTokenManager() returns(bytes32) envfree
    roleBNTManager() returns(bytes32) envfree
    roleVaultManager() returns(bytes32) envfree
    roleFundingManager() returns(bytes32) envfree
    currentPoolFunding(address) returns(uint256) envfree
    getRoleAdmin(bytes32) returns(bytes32) envfree
    poolTokenToUnderlying(uint256) returns(uint256) envfree
    underlyingToPoolToken(uint256) returns(uint256) envfree
}


function requests(env e, address pool){
    requireInvariant bntCorrelation();
    requireInvariant bntMintingLimit(pool);
    requireInvariant zeroCorrelation(e);
}


ghost currentPoolFundingSum() returns uint256 {
    init_state axiom currentPoolFundingSum() == 0;
}

hook Sstore _currentPoolFunding[KEY address id] uint256 funding (uint256 old_funding) STORAGE {
    havoc currentPoolFundingSum assuming 
            currentPoolFundingSum@new() == currentPoolFundingSum@old() + funding - old_funding;
}


// STATUS - verified
// Solvency: total amount of all BNTs should be equal to the sum of BNTs of all pools
invariant bntCorrelation()
    currentPoolFundingSum() == stakedBalance()


// STATUS - verified
// `_currentPoolFunding` cannot exceed `poolFundingLimit`
invariant bntMintingLimit(address pool)
    currentPoolFunding(pool) <= NetSet.poolFundingLimit(pool)
    filtered { f -> f.selector != onFeesCollected(address, uint256, bool).selector }





// STATUS - verified
// If `_stakedBalance` is 0 then `totalSupply` of `poolToken` is 0 too and vice versa (assume only calls from users without any role. Users with manager roles can violated it).
invariant zeroCorrelation(env e)
    stakedBalance() == 0 <=> PoolT.totalSupply() == 0
    {
        preserved with (env e2){
            require e.msg.sender == e2.msg.sender;
            require e.msg.sender != _network();

            bytes32 bntPoolM = roleBNTPoolTokenManager();
            bytes32 bntM = roleBNTManager();
            bytes32 vaultM = roleVaultManager();
            bytes32 funcdingM = roleFundingManager();
            bytes32 assetM = DungeonMaster.roleAssetManager();

            require !hasRole(bntPoolM, e.msg.sender)
                        && !hasRole(bntM, e.msg.sender)
                        && !hasRole(vaultM, e.msg.sender)
                        && !hasRole(funcdingM, e.msg.sender)
                        && !hasRole(assetM, e.msg.sender);
        }
    }


// STATUS - verified
// Only `IBancorNetwork` contract can call `depositFor()`, `withdraw()`, `onFeesCollected()`.
// Proved safe assumption for properties related to tokens changes.
rule networkGodMode(method f, env e) filtered { f -> f.selector == onFeesCollected(address, uint256, bool).selector 
                                                        || f.selector == withdraw(bytes32, address, uint256).selector 
                                                        || f.selector == depositFor(bytes32, address, uint256, bool, uint256).selector} {
    calldataarg args;
    f@withrevert(e, args);
    assert !lastReverted => e.msg.sender == _network(), "Mortal soul cannot get God's power!";
}


// STATUS - verified
// Only pool admin can manage minting, burning and funding operations.
rule almightyAdmin(method f, env e) filtered { f -> f.selector == requestFunding(bytes32, address, uint256).selector
                                            || f.selector == renounceFunding(bytes32, address, uint256).selector
                                            || f.selector == mint(address, uint256).selector
                                            || f.selector == burnFromVault(uint256).selector} {
    calldataarg args;
    f@withrevert(e, args);

    bool isReverted = lastReverted;

    assert  (!isReverted 
                    && (f.selector == requestFunding(bytes32, address, uint256) .selector
                            || f.selector == renounceFunding(bytes32, address, uint256).selector))
            => hasRole(roleFundingManager(), e.msg.sender), "With great power comes great requestFunding/renounceFunding";
    assert  (!isReverted 
                    && f.selector == mint(address, uint256).selector)
            => hasRole(roleBNTManager(), e.msg.sender), "With great power comes great mint";
    assert  (!isReverted 
                    && f.selector == burnFromVault(uint256).selector)
            => hasRole(roleVaultManager(), e.msg.sender), "With great power comes great burnFromVault";
}


// STATUS - verified
// It's impossible to acquire any role from BNTPool contract, except `grantRole()` function. It's checked separately.
// Proved safe assumption for properties related to tokens changes.
rule imposterCheck(method f, env e) filtered{ f -> f.selector != grantRole(bytes32, address).selector } {
    bytes32 bntPoolM = roleBNTPoolTokenManager();
    bytes32 bntM = roleBNTManager();
    bytes32 vaultM = roleVaultManager();
    bytes32 funcdingM = roleFundingManager();
    bytes32 assetM = DungeonMaster.roleAssetManager();

    require !hasRole(bntPoolM, e.msg.sender)
                && !hasRole(bntM, e.msg.sender)
                && !hasRole(vaultM, e.msg.sender)
                && !hasRole(funcdingM, e.msg.sender)
                && !hasRole(assetM, e.msg.sender);

    calldataarg args;
    f(e, args);

    assert !hasRole(bntPoolM, e.msg.sender)
                && !hasRole(bntM, e.msg.sender)
                && !hasRole(vaultM, e.msg.sender)
                && !hasRole(funcdingM, e.msg.sender)
                && !hasRole(assetM, e.msg.sender), "You are sneaky little imposter, aren't you?";
}


// STATUS - verified
// `msg.sender` without admin role cannot grant role to anyone: `grantRole()` will revert in this case.
rule imposterAdminCheck(method f, env e){
    address user;
    bytes32 role;

    require !hasRole(getRoleAdmin(role), e.msg.sender);

    grantRole@withrevert(e, role, user);

    assert lastReverted, "Admin is imposter!";
}


// STATUS - in progress 
// Expected to fail because Bancor doesn't have this protection.
// grantRole() also leads to the violation because user could have soemthing before granting them role
// invariant noMoneyForAdmin(env e, address user)
//     (hasRole(roleBNTPoolTokenManager(), user) || hasRole(roleBNTManager(), user) 
//             || hasRole(roleVaultManager(), user) || hasRole(roleFundingManager(), user) 
//             || hasRole(DungeonMaster.roleAssetManager(), user))
//     => (PoolT.balanceOf(user) == 0 
//             && BntGovern.getBNTBalance(e, user) == 0 
//             && VbntGovern.getBNTBalance(e, user) == 0)
//     {
//         preserved with (env e2){
//             require user != DungeonMaster;
//             require user != _network();
//             require user != currentContract;
//             require BntGovern._token() != VbntGovern._token();
//             // require BntGovern.getToken(e2) != VbntGovern.getToken(e2);
//         }
//     }









// STATUS - in progress. Round off issue. issue with vbnt, init values are picked in the way that calculations produce > 0 value for depositFor(a + b) 
// and 0 for separated deposits: depostFor(a) and DepositFor(b)
// https://vaas-stg.certora.com/output/3106/6560511b6266620250c6/?anonymousKey=3a746426debec45825993efed77dfc7a478b1cd8
// `depositFor()` is additive: `depositFor(a)` + `depositFor(b)` has the same effect as `depositFor(a + b)`
rule depositForAdditivity(env e){
    bytes32 contextId;
    address provider;
    uint256 bntAmount; uint256 bntAmountPart1; uint256 bntAmountPart2;
    bool isMigrating;
    uint256 originalVBNTAmount;
    
    require bntAmount == bntAmountPart1 + bntAmountPart2;
    require BntGovern._token() != VbntGovern._token();

    uint256 providerPTBefore = PoolT.balanceOf(provider);
    uint256 bntBefore = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, provider);

    storage initialStorage = lastStorage;

    depositFor(e, contextId, provider, bntAmount, isMigrating, originalVBNTAmount);

    uint256 providerPTSimple = PoolT.balanceOf(provider);
    uint256 bntSimple = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntSimple = VbntGovern.getBNTBalance(e, provider);

    depositFor(e, contextId, provider, bntAmountPart1, isMigrating, originalVBNTAmount) at initialStorage;
    depositFor(e, contextId, provider, bntAmountPart2, isMigrating, originalVBNTAmount);

    uint256 providerPTComplex = PoolT.balanceOf(provider);
    uint256 bntComplex = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntComplex = VbntGovern.getBNTBalance(e, provider);

    assert providerPTSimple == providerPTComplex, "should be additive (pt)";
    assert bntSimple == bntComplex, "should be additive (bnt)";
    assert vbntSimple == vbntComplex, "should be additive (vbnt)";
}


// STATUS - in progress.
// `withdraw()` is additive: `withdraw(a)` + `withdraw(b)` has the same effect as `withdraw(a + b)` *
// * we don't calculate fees in `_withdrawalAmounts()`, otherwise can found a counterexample where for (a + b)
// fees will be > 0, but for case `a`, then `b`, fees will be 0. Tool doesn't know about migration data passed from other versions. 
rule withdrawAdditivity(env e){
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount; uint256 poolTokenAmountPart1; uint256 poolTokenAmountPart2;
    
    require poolTokenAmount == poolTokenAmountPart1 + poolTokenAmountPart2;
    require BntGovern._token() != VbntGovern._token();

    uint256 providerPTBefore = PoolT.balanceOf(currentContract);
    uint256 bntBefore = BntGovern.getBNTBalance(e, provider);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, currentContract);

    storage initialStorage = lastStorage;

    withdraw(e, contextId, provider, poolTokenAmount);

    uint256 providerPTSimple = PoolT.balanceOf(currentContract);
    uint256 bntSimple = BntGovern.getBNTBalance(e, provider);
    uint256 vbntSimple = VbntGovern.getBNTBalance(e, currentContract);

    withdraw(e, contextId, provider, poolTokenAmountPart1) at initialStorage;
    withdraw(e, contextId, provider, poolTokenAmountPart2);

    uint256 providerPTComplex = PoolT.balanceOf(currentContract);
    uint256 bntComplex = BntGovern.getBNTBalance(e, provider);
    uint256 vbntComplex = VbntGovern.getBNTBalance(e, currentContract);

    assert providerPTSimple == providerPTComplex, "should be additive (pt)";
    assert bntSimple == bntComplex, "should be additive (bnt)";
    assert vbntSimple == vbntComplex, "should be additive (vbnt)";
}


// STATUS - verified 
// After a successful request funding operation for pool, _currentPoolFunding(pool) > 0 and must increase up to the funding limit.
rule increaseAfterRequestFunding(env e){
    bytes32 contextId;
    uint256 bntAmount;
    address pool;

    uint256 poolFundingBefore = currentPoolFunding(pool);  // what is Token called pool?

    requestFunding(e, contextId, pool, bntAmount);

    uint256 poolFundingAfter = currentPoolFunding(pool);

    assert poolFundingAfter > 0, "From zero to hero";
    assert poolFundingAfter <= NetSet.poolFundingLimit(pool), "Exceeded funding limit";
    assert poolFundingBefore < poolFundingAfter, "You should be better than me!";
}


// STATUS - verified 
// After a successful renounce funding operation for pool, _currentPoolFunding(pool) >=0 and must decrease if was greater than 0.
rule increaseAfterRenounceFunding(env e){
    bytes32 contextId;
    uint256 bntAmount;
    address pool;

    uint256 poolFundingBefore = currentPoolFunding(pool);  // what is Token called pool?

    renounceFunding(e, contextId, pool, bntAmount);

    uint256 poolFundingAfter = currentPoolFunding(pool);

    assert poolFundingAfter >= 0, "From zero to hero";
    assert poolFundingBefore > 0 => poolFundingBefore > poolFundingAfter, "You should be better than me!";
    assert poolFundingBefore == 0 => poolFundingBefore == poolFundingAfter, "You should be better than me!";
}


// STATUS - verified 
// _currentPoolFunding should not change after a BNT withdrawal
rule untouchableCurrentPoolFunding(env e){
    address pool;
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount;

    uint256 poolFundingBefore = currentPoolFunding(pool);

    withdraw(e, contextId, provider, poolTokenAmount);

    uint256 poolFundingAfter = currentPoolFunding(pool);

    assert poolFundingBefore == poolFundingAfter, "How dare you touch my treasure?";
}


// STATUS - verified
rule withdrawUnitTest(env e) {
    address pool;
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount;

    requests(e, pool);

    require provider != e.msg.sender && provider != _network() 
                && provider != currentContract && _network() != currentContract;

    uint256 providerPTBefore = PoolT.balanceOf(currentContract);
    uint256 bntBefore = BntGovern.getBNTBalance(e, provider);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, currentContract);
    uint256 withAmount = withdrawalAmount(poolTokenAmount);

    withdraw(e, contextId, provider, poolTokenAmount);

    uint256 providerPTAfter = PoolT.balanceOf(currentContract);
    uint256 bntAfter = BntGovern.getBNTBalance(e, provider);
    uint256 vbntAfter = VbntGovern.getBNTBalance(e, currentContract);

    assert bntBefore + withAmount == bntAfter, "Wrong BNT update";
    assert vbntBefore - poolTokenAmount == vbntAfter, "Wrong VBNT update";
    assert providerPTBefore + poolTokenAmount == providerPTAfter, "Wrong PT update"; 
}


// STATUS - verified 
// If `provider` is `msg.sender`, but not `_network`, withdraw reverts.
rule providerCheck(env e){
    address pool;
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount;

    withdraw@withrevert(e, contextId, provider, poolTokenAmount);
    bool isReverted = lastReverted;

    assert (provider == e.msg.sender && provider != _network()) => isReverted, "check failed";
}


// STATUS - verified 
// A user’s PT balance can increase/decrease if and only if he stakes/withdraws BNT in the pool.
rule doppelganger(method f, env e) {
    address provider;

    require provider != _network();
    require provider != currentContract;
    require f.selector == onFeesCollected(address, uint256, bool).selector 
                || f.selector == withdraw(bytes32, address, uint256).selector 
                || f.selector == depositFor(bytes32, address, uint256, bool, uint256).selector
            => provider != e.msg.sender;

    uint256 providerPTBefore = PoolT.balanceOf(provider);

    calldataarg args;
    f(e, args);

    uint256 providerPTAfter = PoolT.balanceOf(provider);

    assert providerPTBefore > providerPTAfter 
                    => (f.selector == withdraw(bytes32, address, uint256).selector 
                            )
            , "no withdraw doppelganger";
    assert providerPTBefore < providerPTAfter => f.selector == depositFor(bytes32, address, uint256, bool, uint256).selector || f.selector == withdrawFunds(address, address, uint256).selector, "no depositFor doppelganger";
}


// STATUS - verified
// during withdraw only BNT balance of a provider should increase 
rule bntMintLonelyUserIncrease(env e) {
    address provider; address randUser; address pool;
    bytes32 contextId;
    uint256 poolTokenAmount;

    requests(e, pool);
    require randUser != e.msg.sender && randUser != _network() && randUser != currentContract;

    uint256 randUserBalanceBefore = BntGovern.getBNTBalance(e, randUser);

    require withdraw(e, contextId, provider, poolTokenAmount) > 0;

    uint256 randUserBalanceAfter = BntGovern.getBNTBalance(e, randUser);

    assert randUserBalanceBefore == randUserBalanceAfter => provider != randUser, "Two-Face is back";
}


// STATUS - verified
// `poolTokenToUnderlying()` then `underlyingToPoolToken()` and vice versa case, should return the same amount as at the beginning.
rule toTheMoonAndBack() {
    uint256 poolTokenAmount;
    uint256 bntAmount;

    assert poolTokenAmount == underlyingToPoolToken(poolTokenToUnderlying(poolTokenAmount)), "wrong poolTokenAmount conversion";
    assert bntAmount == poolTokenToUnderlying(underlyingToPoolToken(bntAmount)), "wrong bntAmount conversion";
}


// STATUS - verified
// what is correct assert to chec that only one acc balance was changed?
// Fees accrued by trading, must count in staked balance.
rule onFeesCollectedUnitTest(env e){
    address pool;
    address randomPool;
    uint256 feeAmount;
    bool isTradeFee;

    uint256 stakedBalanceBefore = stakedBalance();
    uint256 currentPoolFundingBefore = currentPoolFunding(randomPool);

    onFeesCollected(e, pool, feeAmount, isTradeFee);

    uint256 stakedBalanceAfter = stakedBalance();
    uint256 currentPoolFundingAfter = currentPoolFunding(randomPool);

    assert stakedBalanceBefore + feeAmount == stakedBalanceAfter, "stakedBalance wrong increase";
    assert currentPoolFundingBefore == currentPoolFundingAfter && isTradeFee == true && feeAmount > 0 => pool != randomPool, "Two-Face is back";
}


// STATUS - verified
// Staking BNT by a user is possible only if the protocol has enough PTs to provide in exchange.
rule cofferIsEmptyMyLiege(env e) {
    bytes32 contextId;
    address provider;
    uint256 bntAmount;
    bool isMigrating;
    uint256 originalVBNTAmount;

    uint256 providerPTBefore = PoolT.balanceOf(currentContract);

    depositFor@withrevert(e, contextId, provider, bntAmount, isMigrating, originalVBNTAmount);

    bool isReverted = lastReverted;

    assert providerPTBefore < underlyingToPoolToken(bntAmount) => isReverted, "Huston, we have a problem";
}


