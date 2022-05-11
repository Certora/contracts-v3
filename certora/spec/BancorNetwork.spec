import "../helpers/erc20.spec"

using DummyPoolColA as PoolColA
using DummyPoolColB as PoolColB
using DummyERC20A as tokenA
using DummyERC20B as tokenB
using DummyPoolTokenA as ptA
using MasterVault as mVault


////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {
    // BancorNetwork
    _poolCollection(address) returns (address) envfree
    depositForPermitted(address,address,uint256,uint256,uint8,bytes32,bytes32)
    returns (uint256) envfree

    // Pool collection
    depositFor(bytes32,address,address,uint256) returns (uint256) => DISPATCHER(true)
    tradeByTargetAmount(bytes32,address,address,uint256,uint256)
                returns (uint256,uint256,uint256) => DISPATCHER(true)
    tradeBySourceAmount(bytes32,address,address,uint256,uint256)
                returns (uint256,uint256,uint256) => DISPATCHER(true)
    poolType() returns (uint16) => DISPATCHER(true)
    poolCount() returns (uint256) => DISPATCHER(true)
    createPool(address) => DISPATCHER(true)

    // Others
    permit(address,address,uint256,uint256,uint8,bytes32,bytes32) => DISPATCHER(true)
    withdrawFunds(address, address, uint256) => DISPATCHER(true) 
    minLiquidityForTrading() returns(uint256) => DISPATCHER(true)
    networkFeePPM() returns(uint32) => DISPATCHER(true)
    burn(uint256) => DISPATCHER(true)
    burn(address, uint256) => DISPATCHER(true)
    burnFrom(address, uint256) => DISPATCHER(true)
    burnFromVault(uint256) => DISPATCHER(true)
    mint(address, uint256) => DISPATCHER(true)
    destroy(address, uint256) => DISPATCHER(true)
    reserveToken() returns (address) => DISPATCHER(true)
}

////////////////////////////////////////////////////////////////////////////
//                       Ghosts and definitions                           //
////////////////////////////////////////////////////////////////////////////

// TODO: add ghosts as necessary

////////////////////////////////////////////////////////////////////////////
//                       Invariants                                       //
////////////////////////////////////////////////////////////////////////////

// TODO: Add invariants; document them in reports/ExampleReport.md

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

rule reachability(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

rule checkinitWithdraw(uint amount)
{
    env e;
    initWithdrawal(e,ptA, amount);
    assert false;
}

rule checkcancelWithdrawal(uint id)
{
    env e;
    cancelWithdrawal(e,id);
    assert false;
}

rule tradeBalancesChanged(uint amount, address beneficiary)
{
    env e;
    uint256 maxSourceAmount;
    uint256 deadline;
    require e.msg.sender != mVault;
    tokensPoolCollectionsSetup(tokenA,tokenB);

    uint256 balanceA1 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB1 = tokenB.balanceOf(e,e.msg.sender);

    require balanceB1 + amount < max_uint;

    tradeByTargetAmount(e,tokenA,tokenB,
        amount,maxSourceAmount,deadline,beneficiary);

    uint256 balanceA2 = tokenA.balanceOf(e,e.msg.sender);
    uint256 balanceB2 = tokenB.balanceOf(e,e.msg.sender);
    
    //assert balanceA2 < balanceA1;
    assert balanceB1 + amount == balanceB2;
}

////////////////////////////////////////////////////////////////////////////
//                       Helper Functions                                 //
////////////////////////////////////////////////////////////////////////////
function myXor(bool A, bool B) returns bool
{
    return (!A && B) || (!B && A);
}

function tokenInPoolCollectionA(address tkn) returns bool
{
    return _poolCollection(tkn) == PoolColA;
}

function tokenInPoolCollectionB(address tkn) returns bool
{
    return _poolCollection(tkn) == PoolColB;
}
// For any two different tokens, we require them to either be in the same
// pool collection or different ones. Note that any two pool collections cannot
// share the same token.
function tokensPoolCollectionsSetup(address tknA, address tknB)
{
    require tknA != tknB;
    require myXor(tokenInPoolCollectionA(tknA),tokenInPoolCollectionB(tknA));
    require myXor(tokenInPoolCollectionA(tknB),tokenInPoolCollectionB(tknB));
}