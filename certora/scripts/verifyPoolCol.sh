python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/PoolCollection.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/BNTPool.sol certora/munged/network/NetworkSettings.sol certora/munged/pools/PoolToken.sol \
    certora/munged/vaults/MasterVault.sol certora/harness/ERC20BurnableHarness.sol \
    certora/munged/pools/PoolTokenFactory.sol certora/munged/network/BancorNetwork.sol \
    certora/helpers/Receiver1.sol certora/helpers/Receiver2.sol \
    --verify PoolCollection:certora/spec/PoolCol.spec \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "PoolCol no dispatcher for createPoolToken sum check"


    # certora/harness/OwnedHarness.sol