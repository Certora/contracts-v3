import "./BNTPool.spec"

use invariant bntCorrelation
use invariant bntMintingLimit


// STATUS - verified
// `depositFor()` is additive: `depositFor(a)` + `depositFor(b)` has the same effect as `depositFor(a + b)`
// migrations isn't considered. fees in `_withdrawalAmounts()` aren't considered.
rule depositForAdditivity(env e){
    bytes32 contextId;
    address provider;
    uint256 bntAmount; uint256 bntAmount1; uint256 bntAmount2;
    bool isMigrating;
    uint256 originalVBNTAmount;
    
    require bntAmount == bntAmount1 + bntAmount2;
    require BntGovern._token() != VbntGovern._token();

    require isMigrating == false;

    uint256 providerPTBefore = PoolT.balanceOf(provider);
    uint256 bntBefore = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, provider);

    storage initialStorage = lastStorage;

    depositFor(e, contextId, provider, bntAmount, isMigrating, originalVBNTAmount);

    uint256 providerPTSimple = PoolT.balanceOf(provider);
    uint256 bntSimple = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntSimple = VbntGovern.getBNTBalance(e, provider);

    depositFor(e, contextId, provider, bntAmount1, isMigrating, originalVBNTAmount) at initialStorage;
    depositFor(e, contextId, provider, bntAmount2, isMigrating, originalVBNTAmount);

    uint256 providerPTComplex = PoolT.balanceOf(provider);
    uint256 bntComplex = BntGovern.getBNTBalance(e, currentContract);
    uint256 vbntComplex = VbntGovern.getBNTBalance(e, provider);

    assert providerPTSimple == providerPTComplex, "should be additive (pt)";
    assert bntSimple == bntComplex, "should be additive (bnt)";
    assert vbntSimple == vbntComplex, "should be additive (vbnt)";
}


// STATUS - verified
// `withdraw()` is additive: `withdraw(a)` + `withdraw(b)` has the same effect as `withdraw(a + b)` *
// * we don't calculate fees in `_withdrawalAmounts()`, otherwise the tool can found a counterexample where for (a + b)
// fees will be > 0, but for case `a`, then `b`, fees will be 0 because of round off error in `mulDivF()`
rule withdrawAdditivity(env e){
    bytes32 contextId;
    address provider;
    uint256 poolTokenAmount; uint256 poolTokenAmount1; uint256 poolTokenAmount2;
    uint256 originalPoolTokenAmount; uint256 originalPoolTokenAmount1; uint256 originalPoolTokenAmount2;
    
    require poolTokenAmount == poolTokenAmount1 + poolTokenAmount2;
    require originalPoolTokenAmount == originalPoolTokenAmount1 + originalPoolTokenAmount2;
    require BntGovern._token() != VbntGovern._token();

    uint256 providerPTBefore = PoolT.balanceOf(currentContract);
    uint256 bntBefore = BntGovern.getBNTBalance(e, provider);
    uint256 vbntBefore = VbntGovern.getBNTBalance(e, currentContract);

    storage initialStorage = lastStorage;

    withdraw(e, contextId, provider, poolTokenAmount, originalPoolTokenAmount);

    uint256 providerPTSimple = PoolT.balanceOf(currentContract);
    uint256 bntSimple = BntGovern.getBNTBalance(e, provider);
    uint256 vbntSimple = VbntGovern.getBNTBalance(e, currentContract);

    withdraw(e, contextId, provider, poolTokenAmount1, originalPoolTokenAmount1) at initialStorage;
    withdraw(e, contextId, provider, poolTokenAmount2, originalPoolTokenAmount2);

    uint256 providerPTComplex = PoolT.balanceOf(currentContract);
    uint256 bntComplex = BntGovern.getBNTBalance(e, provider);
    uint256 vbntComplex = VbntGovern.getBNTBalance(e, currentContract);

    assert providerPTSimple == providerPTComplex, "should be additive (pt)";
    assert bntSimple == bntComplex, "should be additive (bnt)";
    assert vbntSimple == vbntComplex, "should be additive (vbnt)";
}


// STATUS - verified
// `poolTokenToUnderlying()` then `underlyingToPoolToken()` and vice versa case, should return the same amount as at the beginning.
rule toTheMoonAndBack() {
    uint256 poolTokenAmount;
    uint256 bntAmount;

    assert poolTokenAmount == underlyingToPoolToken(poolTokenToUnderlying(poolTokenAmount)), "wrong poolTokenAmount conversion";
    assert bntAmount == poolTokenToUnderlying(underlyingToPoolToken(bntAmount)), "wrong bntAmount conversion";
}
