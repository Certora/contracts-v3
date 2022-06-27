certoraRun.py certora/harness/BNTPoolHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/network/NetworkSettings.sol certora/munged/pools/PoolToken.sol certora/munged/vaults/MasterVault.sol \
    certora/helpers/DummyERC20bnt.sol certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    certora/munged/helpers/TestUpgradeable.sol \
    --verify BNTPoolHarness:certora/spec/BNTPoolNoRemainder.spec \
    --link  BNTPoolHarness:_poolToken=PoolToken \
            BNTPoolHarness:_bnt=DummyERC20bnt \
            BNTPoolHarness:_bntGovernance=DummyTokenGovernanceA \
            BNTPoolHarness:_vbntGovernance=DummyTokenGovernanceB \
            BNTPoolHarness:_masterVault=MasterVault \
            MasterVault:_bntGovernance=DummyTokenGovernanceA \
            MasterVault:_vbntGovernance=DummyTokenGovernanceB \
    --solc solc8.13 \
    --cloud \
    --optimistic_loop \
    --settings -divideNoRemainder=true \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "BNTPoolNoRemainder rules"
