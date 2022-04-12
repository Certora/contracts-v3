python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/BNTPool.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/PoolToken.sol certora/munged/network/NetworkSettings.sol certora/harness/ERC20BurnableHarness.sol \
    certora/munged/vaults/MasterVault.sol certora/harness/OwnedHarness.sol node_modules/@bancor/token-governance/contracts/TokenGovernance.sol \
    --verify BNTPool:certora/spec/BNTPool.spec \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "BNTPool sum check"