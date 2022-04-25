import "../helpers/erc20.spec"

using DummyERC20A as tokenA
using DummyERC20B as tokenB
using DummyPoolTokenA as ptA
using DummyPoolTokenA as ptB

methods {
    renounceFunding(bytes32, address, uint256) => DISPATCHER(true)
    // requestFunding(bytes32, address, uint256) => DISPATCHER(true)
    // availableFunding(address) returns(uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) envfree => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    acceptOwnership() => DISPATCHER(true)
    withdrawFunds(address, address, uint256) => DISPATCHER(true)   
    isTokenWhitelisted(address) returns(bool) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    createPoolToken(address) returns(address) => DISPATCHER(true)       // caused issues
    // latestPoolCollection(uint16) returns(address) => DISPATCHER(true) lets have it nondet
    issue(address, uint256) => DISPATCHER(true)
    transferOwnership(address) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    // receive() => DISPATCHER(true)

    poolToken(address) returns(address) envfree

    migratePoolOut(address, address)
}


function setUp() {
    require poolToken(tokenA) == ptA || poolToken(tokenA) == ptB;
    require poolToken(tokenB) == ptA || poolToken(tokenB) == ptB;
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


rule sanity(method f)
{
	env e;
	calldataarg args;
	santasLittleHelper(f, e);
	assert false;
}

rule more_poolTokens_less_TKN(method f){
    env e;
    require e.msg.sender != currentContract && e.msg.sender != _masterVault(e);
    calldataarg args;
    setUp();

    uint256 tkn_balance = tokenA.balanceOf(e,e.msg.sender);
    uint256 poolToken_balance = ptA.balanceOf(e,e.msg.sender);

    f(e,args);

    uint256 tkn_balance2 = tokenA.balanceOf(e,e.msg.sender);
    uint256 poolToken_balance2 = ptA.balanceOf(e,e.msg.sender);

    assert tkn_balance2 > tkn_balance <=> poolToken_balance > poolToken_balance2;
    assert tkn_balance2 < tkn_balance <=> poolToken_balance < poolToken_balance2;
}