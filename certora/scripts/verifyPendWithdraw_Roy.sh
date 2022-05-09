py ../../EVMVerifier/scripts/certoraRun.py \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/munged/pools/BNTPool.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/munged/pools/PoolToken.sol \
    certora/helpers/DummyPoolTokenA.sol \
    certora/helpers/DummyPoolTokenB.sol \
    certora/munged/network/BancorNetwork.sol \
    --verify PendingWithdrawalsHarness:./certora/spec/PendWithdraw_Roy.spec \
    --link PendingWithdrawalsHarness:_bntPool=BNTPool \
    PendingWithdrawalsHarness:_network=BancorNetwork \
    BNTPool:_poolToken=PoolToken \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --rule TotalRequestPTlessThanSupply \
    --send_only \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
    @bancor=node_modules/@bancor \
    --msg "TotalRequestPTlessThanSupply"
