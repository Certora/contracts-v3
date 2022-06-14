certoraRun.py \
    certora/harness/PendingWithdrawalsHarness.sol \
    certora/helpers/DummyERC20A.sol \
    certora/helpers/DummyERC20bnt.sol \
    certora/munged/pools/BNTPool.sol \
    certora/harness/PoolCollectionHarness.sol \
    certora/munged/pools/PoolToken.sol \
    certora/helpers/DummyPoolTokenA.sol \
    certora/helpers/DummyPoolTokenB.sol \
    certora/munged/network/BancorNetwork.sol \
    --verify PendingWithdrawalsHarness:./certora/spec/PendWithdraw_Roy.spec \
    --link  PendingWithdrawalsHarness:_bntPool=BNTPool \
            PendingWithdrawalsHarness:_bnt=DummyERC20bnt \
            PendingWithdrawalsHarness:_network=BancorNetwork \
            BNTPool:_poolToken=PoolToken \
    --solc solc8.13 \
    --staging \
    --rule_sanity advanced \
    --send_only \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin \
            @bancor=node_modules/@bancor \
    --rule "$1" \
    --msg "$1 commmented delete"
#--method "completeWithdrawal(bytes32,address,uint256)" \
