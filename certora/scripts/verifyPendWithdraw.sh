py ../../EVMVerifier/scripts/certoraRun.py \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20bnt.sol \
    certora/munged/pools/BNTPool.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/munged/pools/PoolToken.sol \
    certora/helpers/DummyPoolTokenA.sol \
    certora/helpers/DummyPoolTokenB.sol \
    certora/munged/network/BancorNetwork.sol \
    --verify PendingWithdrawalsHarness:./certora/spec/PendWithdraw.spec \
    --link  PendingWithdrawalsHarness:_bntPool=BNTPool \
            PendingWithdrawalsHarness:_bnt=DummyERC20bnt \
            PendingWithdrawalsHarness:_network=BancorNetwork \
            BNTPool:_poolToken=PoolToken \
    --solc solc8.13 \
    --cloud \
    --rule_sanity basic \
    --send_only \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
            @bancor=node_modules/@bancor \
    --msg "PendingWithdrawals rules Roy Fix"
