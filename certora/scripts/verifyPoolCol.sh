if [[ "$1" ]]
then
    RULE="--rule $1"
fi

    certoraRun.py  node_modules/@bancor/token-governance/contracts/tests/MintableToken.sol certora/harness/PoolCollectionHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
     certora/munged/pools/BNTPool.sol certora/munged/network/NetworkSettings.sol certora/munged/network/BancorNetwork.sol \
    certora/munged/pools/PoolTokenFactory.sol certora/munged/pools/PoolToken.sol certora/helpers/DummyERC20bnt.sol \
    certora/helpers/DummyPoolTokenA.sol certora/helpers/DummyPoolTokenB.sol certora/munged/vaults/MasterVault.sol \
    certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    certora/munged/vaults/ExternalProtectionVault.sol \
    --verify PoolCollectionHarness:certora/spec/PoolCol.spec \
    --link  PoolCollectionHarness:_bnt=DummyERC20bnt \
            PoolCollectionHarness:_masterVault=MasterVault \
            PoolCollectionHarness:_bntPool=BNTPool \
            PoolCollectionHarness:_externalProtectionVault=ExternalProtectionVault \
            BNTPool:_masterVault=MasterVault \
            MasterVault:_bntGovernance=DummyTokenGovernanceA \
            MasterVault:_vbntGovernance=DummyTokenGovernanceB \
    --solc solc8.13 \
    --staging \
    $RULE  \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "PoolCol - $RULE"

#    --rule_sanity advanced \
# certora/munged/network/NetworkSettings.sol PoolCollectionHarness:_network=BancorNetwork \ 
# python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/PoolCollection.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
#     certora/munged/pools/BNTPool.sol certora/munged/network/NetworkSettings.sol certora/munged/pools/PoolToken.sol \
#     certora/munged/vaults/MasterVault.sol certora/harness/ERC20BurnableHarness.sol \
#     certora/munged/pools/PoolTokenFactory.sol certora/munged/network/BancorNetwork.sol \
#     certora/helpers/Receiver1.sol certora/helpers/Receiver2.sol certora/helpers/DummyPoolTokenA.sol certora/helpers/DummyPoolTokenB.sol \
#     --verify PoolCollection:certora/spec/PoolCol.spec \
#     --solc solc8.13 \
#     --staging \
#     --optimistic_loop \
#     --packages_path node_modules \
#     --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
#     --msg "PoolCol no dispatcher for createPoolToken, testing SetUp sum check"


    # certora/harness/OwnedHarness.sol