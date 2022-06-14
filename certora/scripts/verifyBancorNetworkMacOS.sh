certoraRun.py \
    certora/harness/BancorNetworkHarness.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/munged/pools/BNTPool.sol \
    certora/munged/vaults/MasterVault.sol \
    certora/munged/vaults/ExternalProtectionVault.sol \
    certora/munged/network/NetworkSettings.sol \
    certora/munged/pools/PoolTokenFactory.sol \
    certora/munged/helpers/TestFlashLoanRecipient.sol \
    certora/munged/pools/PoolMigrator.sol \
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
    --verify BancorNetworkHarness:certora/spec/BancorNetwork.spec \
    --link  BancorNetworkHarness:_bnt=DummyERC20bnt \
            BancorNetworkHarness:_vbnt=DummyERC20vbnt \
            BancorNetworkHarness:_bntGovernance=DummyTokenGovernanceA \
            BancorNetworkHarness:_vbntGovernance=DummyTokenGovernanceB \
            BancorNetworkHarness:_bntPool=BNTPool \
            BancorNetworkHarness:_bntPoolToken=DummyPoolTokenBNT \
            BancorNetworkHarness:_masterVault=MasterVault \
            BancorNetworkHarness:_externalProtectionVault=ExternalProtectionVault \
            BancorNetworkHarness:_pendingWithdrawals=PendingWithdrawalsHarness \
            BancorNetworkHarness:_poolMigrator=PoolMigrator \
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
            PendingWithdrawalsHarness:_network=BancorNetworkHarness \
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
    --staging jtoman/bancor-opt \
    --send_only \
    --rule "$1" \
    --rule_sanity advanced \
    --disable_auto_cache_key_gen \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
            @bancor=node_modules/@bancor \
    --settings -enableEqualitySaturation=false,-divideNoRemainder=true, -optimistic_fallback \
    --msg "$1 with no remainder"

#DummyPoolColA:_bnt=DummyERC20bnt \
#DummyPoolColA:_masterVault=MasterVault \
#DummyPoolColA:_bntPool=BNTPool \
#DummyPoolColA:_externalProtectionVault=ExternalProtectionVault \
#certora/helpers/DummyPoolColA.sol \
#certora/helpers/DummyPoolColB.sol \
#--settings -divideNoRemainder=true \
