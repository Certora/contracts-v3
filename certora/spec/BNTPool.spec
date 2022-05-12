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

    _poolToken() returns(address) envfree
    _stakedBalance() returns(uint256) envfree
    
    _bnt() returns(address) envfree
    _bntGovernance() returns(address) envfree
    _vbntGovernance() returns(address) envfree
    _network() returns(address) envfree

    onFeesCollected(address, uint256, bool)
    withdraw(bytes32, address, uint256) returns(uint256)
    depositFor(bytes32, address, uint256, bool, uint256) returns(uint256)
    requestFunding(bytes32, address, uint256)
    renounceFunding(bytes32, address, uint256)
    grantRole(bytes32, address)

    withdrawalAmount(uint256) returns(uint256) envfree
    roleBNTPoolTokenManager() returns(bytes32) envfree
    roleBNTManager() returns(bytes32) envfree
    roleVaultManager() returns(bytes32) envfree
    roleFundingManager() returns(bytes32) envfree
    currentPoolFunding(address) returns(uint256) envfree
    getRoleAdmin(bytes32) returns(bytes32) envfree
}


function preSet(env e){
    require _bntGovernance() == BntGovern;
    require _vbntGovernance() == VbntGovern;
    require _poolToken() == PoolT;
    require _bntGovernance() != _vbntGovernance();
    require _bntGovernance() != _poolToken();
    require _poolToken() != _vbntGovernance();
}


ghost currentPoolFundingSum() returns uint256 {
    init_state axiom currentPoolFundingSum() == 0;
}

hook Sstore _currentPoolFunding[KEY address id] uint256 funding (uint256 old_funding) STORAGE {
    havoc currentPoolFundingSum assuming 
            currentPoolFundingSum@new() == currentPoolFundingSum@old() + funding - old_funding;
}


invariant bntCorrelation()
    currentPoolFundingSum() == _stakedBalance()


invariant bntMintingLimit(address pool)
    currentPoolFunding(pool) <= NetSet.poolFundingLimit(pool)
    filtered { f -> f.selector != onFeesCollected(address, uint256, bool).selector }





// STATUS - in progress 
// If `_stakedBalance` is 0 then `totalSupply` of `poolToken` is 0 too and vice versa.
invariant zeroCorrelation(env e)
    _stakedBalance() == 0 <=> PoolT.totalSupply() == 0
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
rule networkGodMode(method f, env e) filtered{ f -> f.selector == onFeesCollected(address, uint256, bool).selector 
                                                        || f.selector == withdraw(bytes32, address, uint256).selector 
                                                        || f.selector == depositFor(bytes32, address, uint256, bool, uint256).selector} {
    calldataarg args;
    f@withrevert(e, args);
    assert !lastReverted => e.msg.sender == _network(), "Mortal soul cannot get God's power!";
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







// STATUS - in progress (round of issue)
// https://vaas-stg.certora.com/output/3106/e81a6f5d3a370750fe76/?anonymousKey=9483d5c9e1a8de0c6eb2f2ff32f58a620ac8fdc4
// `depositFor()` is additive: depositFor(a) + depositFor(b) has the same effect as depositFor(a + b)
rule depositForAdditivity(env e){
    bytes32 contextId;
    address provider;
    uint256 bntAmount; uint256 bntAmountPart1; uint256 bntAmountPart2;
    bool isMigrating;
    uint256 originalVBNTAmount;
    
    require bntAmount == bntAmountPart1 + bntAmountPart2;

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


rule withdrawUnitTest(env e) {
    address pool;
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount;

    uint256 providerPTBefore = PoolT.balanceOf(provider);
    uint256 bntBefore = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, provider);
    uint256 withAmount = withdrawalAmount(poolTokenAmount);

    withdraw(e, contextId, provider, poolTokenAmount);

    uint256 providerPTAfter = PoolT.balanceOf(provider);
    uint256 bntAfter = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntAfter = VbntGovern.getBNTBalance(e, provider);

    assert bntBefore + withAmount == bntAfter, "Wrong BNT update";
    assert vbntBefore + poolTokenAmount == vbntAfter, "Wrong VBNT update";
    assert providerPTBefore + poolTokenAmount == providerPTAfter, "Wrong PT update"; 
}


rule doppelganger(method f, env e) {
    address provider;

    uint256 providerPTBefore = PoolT.balanceOf(provider);

    calldataarg args;
    f(e, args);

    uint256 providerPTAfter = PoolT.balanceOf(provider);

    assert providerPTBefore > providerPTAfter => f.selector == withdraw(bytes32, address, uint256).selector, "no withdraw doppelganger";
    assert providerPTBefore < providerPTAfter => f.selector == depositFor(bytes32, address, uint256, bool, uint256).selector, "no depositFor doppelganger";
}



