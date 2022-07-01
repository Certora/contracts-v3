certoraRun.py certora/munged/pools/BNTPool.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/network/NetworkSettings.sol certora/munged/pools/PoolToken.sol certora/munged/vaults/MasterVault.sol \
    certora/helpers/DummyERC20bnt.sol certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    certora/munged/helpers/TestUpgradeable.sol \
    --verify BNTPool:certora/spec/BNTPool.spec \
    --link  BNTPool:_poolToken=PoolToken \
            BNTPool:_bnt=DummyERC20bnt \
            BNTPool:_bntGovernance=DummyTokenGovernanceA \
            BNTPool:_vbntGovernance=DummyTokenGovernanceB \
            BNTPool:_masterVault=MasterVault \
            MasterVault:_bntGovernance=DummyTokenGovernanceA \
            MasterVault:_vbntGovernance=DummyTokenGovernanceB \
    --solc solc8.13 \
    --cloud \
    --optimistic_loop \
    --rule_sanity advanced \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "BNTPool rules"
