certoraRun.py certora/helpers/Receiver1.sol node_modules/@bancor/token-governance/contracts/tests/MintableToken.sol certora/harness/PoolCollectionHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/BNTPool.sol certora/munged/network/NetworkSettings.sol certora/munged/network/BancorNetwork.sol \
    certora/munged/pools/PoolTokenFactory.sol certora/munged/pools/PoolToken.sol certora/helpers/DummyERC20bnt.sol \
    certora/helpers/DummyPoolTokenA.sol certora/helpers/DummyPoolTokenB.sol \
    certora/helpers/DummyPoolTokenBNT.sol certora/munged/vaults/MasterVault.sol \
    certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    certora/munged/vaults/ExternalProtectionVault.sol \
    --verify PoolCollectionHarness:certora/spec/PoolCol.spec \
    --link  PoolCollectionHarness:_bnt=DummyERC20bnt \
            PoolCollectionHarness:_masterVault=MasterVault \
            PoolCollectionHarness:_bntPool=BNTPool \
            PoolCollectionHarness:_externalProtectionVault=ExternalProtectionVault \
            BNTPool:_masterVault=MasterVault \
            BNTPool:_poolToken=PoolToken \
            BNTPool:_bnt=DummyERC20bnt \
            BNTPool:_bntGovernance=DummyTokenGovernanceA \
            BNTPool:_vbntGovernance=DummyTokenGovernanceB \
            MasterVault:_bntGovernance=DummyTokenGovernanceA \
            MasterVault:_vbntGovernance=DummyTokenGovernanceB \
            MasterVault:_bnt=DummyERC20bnt \
    --solc solc8.13 \
    --staging \
    --settings -t=1600,-divideNoRemainder=true,-enableEqualitySaturation=false,-solver=z3 \
    --rule_sanity advanced \
    --disable_auto_cache_key_gen \
    --optimistic_loop \
    --send_only \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --rule "$1" \
    --msg "PoolCol - $1"
