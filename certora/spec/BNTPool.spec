import "../helpers/erc20.spec"

using TokenGovernance as TG

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
    _bntGovernance() returns(address) envfree
}

rule sanity(method f)
{
    // require _bntGovernance() == TG;
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}