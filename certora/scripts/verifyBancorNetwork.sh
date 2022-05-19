py ../../EVMVerifier/scripts/certoraRun.py \
    certora/munged/network/BancorNetwork.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/munged/pools/BNTPool.sol \
    certora/munged/vaults/MasterVault.sol \
    certora/munged/vaults/ExternalProtectionVault.sol \
    certora/munged/network/NetworkSettings.sol \
    \
    \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyPoolTokenA.sol \
    certora/helpers/DummyPoolTokenB.sol \
    certora/helpers/DummyTokenGovernanceA.sol \
    certora/helpers/DummyTokenGovernanceB.sol \
    certora/helpers/DummyERC20bnt.sol \
    certora/helpers/DummyERC20vbnt.sol \
    certora/helpers/DummyPoolTokenBNT.sol \
    certora/helpers/Receiver1.sol \
    \
    \
    --verify BancorNetwork:certora/spec/BancorNetwork.spec \
    --link  BancorNetwork:_bnt=DummyERC20bnt \
            BancorNetwork:_vbnt=DummyERC20vbnt \
            BancorNetwork:_bntGovernance=DummyTokenGovernanceA \
            BancorNetwork:_vbntGovernance=DummyTokenGovernanceB \
            BancorNetwork:_bntPool=BNTPool \
            BancorNetwork:_bntPoolToken=DummyPoolTokenBNT \
            BancorNetwork:_masterVault=MasterVault \
            BancorNetwork:_externalProtectionVault=ExternalProtectionVault \
            BancorNetwork:_pendingWithdrawals=PendingWithdrawalsHarness \
            \
            \
            PoolCollectionHarness:_bnt=DummyERC20bnt \
            PoolCollectionHarness:_masterVault=MasterVault \
            PoolCollectionHarness:_bntPool=BNTPool \
            PoolCollectionHarness:_externalProtectionVault=ExternalProtectionVault \
            \
            \
            PendingWithdrawalsHarness:_bnt=DummyERC20bnt \
            PendingWithdrawalsHarness:_bntPool=BNTPool \
            PendingWithdrawalsHarness:_network=BancorNetwork \
            \
            \
            BNTPool:_poolToken=DummyPoolTokenBNT \
            BNTPool:_bnt=DummyERC20bnt \
            BNTPool:_vbnt=DummyERC20vbnt \
            BNTPool:_bntGovernance=DummyTokenGovernanceA \
            BNTPool:_vbntGovernance=DummyTokenGovernanceB \
            BNTPool:_masterVault=MasterVault \
            \
            \
            MasterVault:_bnt=DummyERC20bnt \
            MasterVault:_vbnt=DummyERC20vbnt \
            MasterVault:_bntGovernance=DummyTokenGovernanceA \
            MasterVault:_vbntGovernance=DummyTokenGovernanceB \
            \
            \
            ExternalProtectionVault:_bnt=DummyERC20bnt \
            ExternalProtectionVault:_vbnt=DummyERC20vbnt \
            ExternalProtectionVault:_bntGovernance=DummyTokenGovernanceA \
            ExternalProtectionVault:_vbntGovernance=DummyTokenGovernanceB \
            \
    --solc solc8.13 \
    --staging \
    --send_only \
    --rule afterTradeSumOfTokenBalanceIntact \
    --disable_auto_cache_key_gen \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
    @bancor=node_modules/@bancor \
    --msg "afterTradeSumOfTokenBalanceIntact"

#DummyPoolColA:_bnt=DummyERC20bnt \
#DummyPoolColA:_masterVault=MasterVault \
#DummyPoolColA:_bntPool=BNTPool \
#DummyPoolColA:_externalProtectionVault=ExternalProtectionVault \
#certora/helpers/DummyPoolColA.sol \
#certora/helpers/DummyPoolColB.sol \
#--settings -divideNoRemainder=true \
