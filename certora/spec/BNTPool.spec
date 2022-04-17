import "../helpers/erc20.spec"

using DummyERC20bnt as dummyBNT
using DummyTokenGovernanceA as bntGovern
using DummyTokenGovernanceB as vbntGovern

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

    _bnt() returns(address) envfree
    _bntGovernance() returns(address) envfree
    _vbntGovernance() returns(address) envfree
}


function preSet(){
	require _bnt() == dummyBNT;
    // require _bntGovernance() == bntGovern;
    // require _vbntGovernance() == vbntGovern;
}


rule sanity(method f)
{
    preSet();
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}