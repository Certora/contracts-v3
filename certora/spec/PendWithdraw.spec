import "../helpers/erc20.spec"

using BancorNetwork as BN
using PoolCollection as PC

methods {
    poolTokenToUnderlying(uint256) returns(uint256) => DISPATCHER(true)
    collectionByPool(address) returns(address) => DISPATCHER(true)
    isPoolValid(address) returns(bool) envfree => DISPATCHER(true)
    reserveToken() returns(address) envfree => DISPATCHER(true)
    poolTokenToUnderlying(address, uint256) returns(uint256) => DISPATCHER(true)

    _bntPool() returns(address) envfree
}

rule sanity(method f)
{   
	env e;
	calldataarg args;
    f(e, args);
	assert false;
}
