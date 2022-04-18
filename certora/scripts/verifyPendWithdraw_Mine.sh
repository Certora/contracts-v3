py ../../EVMVerifier/scripts/certoraRun.py \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/helpers/DummyERC20B.sol \
    certora/helpers/DummyERC20A.sol \
    certora/munged/pools/BNTPool.sol \
    certora/munged/pools/PoolCollection.sol \
    certora/munged/pools/PoolToken.sol \
    certora/munged/network/BancorNetwork.sol \
    node_modules/@openzeppelin/contracts/token/ERC20/ERC20.sol \
    --verify PendingWithdrawalsHarness:./certora/spec/PendWithdraw.spec \
    --link PendingWithdrawalsHarness:_bntPool=BNTPool \
    PendingWithdrawalsHarness:_network=BancorNetwork \
    BNTPool:_poolToken=PoolToken \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --rule CancelWithdrawalIntegrity \
    --send_only \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
    @bancor=node_modules/@bancor \
    --msg "CancelWithdrawalIntegrity"