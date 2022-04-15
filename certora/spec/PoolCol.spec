import "../helpers/erc20.spec"

methods {
    renounceFunding(bytes32, address, uint256) => DISPATCHER(true)
    requestFunding(bytes32, address, uint256) => DISPATCHER(true)
    availableFunding(address) returns(uint256) => DISPATCHER(true)
    poolFundingLimit(address) returns(uint256) => DISPATCHER(true)
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) envfree => DISPATCHER(true)
    withdrawalFeePPM() returns(uint32) => DISPATCHER(true)
    acceptOwnership() => DISPATCHER(true)
    withdrawFunds(address, address, uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    isTokenWhitelisted(address) returns(bool) => DISPATCHER(true)
    // createPoolToken(address) returns(address) => DISPATCHER(true)
    latestPoolCollection(uint16) returns(address) => DISPATCHER(true)
    transferOwnership(address) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    receive() => DISPATCHER(true)
}

rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}