py ../../EVMVerifier/scripts/certoraRun.py \
    certora/helpers/Receiver1.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/BNTPool.sol certora/munged/network/NetworkSettings.sol \
    certora/munged/network/BancorNetwork.sol \
    certora/munged/pools/PoolTokenFactory.sol certora/munged/pools/PoolToken.sol \
    certora/helpers/DummyERC20bnt.sol \
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
    --send_only \
    --rule withdrawAll \
    --settings -divideNoRemainder=true \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
    @bancor=node_modules/@bancor \
    --msg "New explicit PCW summary 2"
#--method "tradeBySourceAmount(bytes32,address,address,uint256,uint256)" \
