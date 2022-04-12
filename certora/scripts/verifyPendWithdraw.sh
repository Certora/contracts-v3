python3 ../../EVMVerifier/scripts/certoraRun.py  certora/harness/PendingWithdrawalsHarness.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/pools/BNTPool.sol certora/munged/pools/PoolCollection.sol certora/munged/pools/PoolToken.sol certora/munged/network/BancorNetwork.sol \
    --verify PendingWithdrawalsHarness:certora/spec/PendWithdraw.spec \
    --link PendingWithdrawalsHarness:_bntPool=BNTPool \
    PendingWithdrawalsHarness:_network=BancorNetwork \
    BNTPool:_poolToken=PoolToken \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "PendingWithdrawals sum check"