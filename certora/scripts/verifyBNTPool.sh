python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/BNTPool.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/PoolToken.sol certora/munged/network/NetworkSettings.sol certora/harness/ERC20BurnableHarness.sol \
    certora/munged/vaults/MasterVault.sol \
    node_modules/@bancor/token-governance/contracts/tests/MintableToken.sol certora/helpers/DummyERC20bnt.sol \
    certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    --verify BNTPool:certora/spec/BNTPool.spec \
    --link BNTPool:_poolToken=PoolToken \
    MasterVault:_bntGovernance=DummyTokenGovernanceA \
    MasterVault:_vbntGovernance=DummyTokenGovernanceB \
    BNTPool:_masterVault=MasterVault \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "BNTPool with trying to fix withdraw sum check"

    #      certora/harness/OwnedHarness.sol           node_modules/@bancor/token-governance/contracts/TokenGovernance.sol