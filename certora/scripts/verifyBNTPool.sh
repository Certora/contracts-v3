python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/BNTPool.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
    certora/munged/network/NetworkSettings.sol certora/munged/pools/PoolToken.sol certora/munged/vaults/MasterVault.sol \
    certora/helpers/DummyERC20bnt.sol certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
    --verify BNTPool:certora/spec/BNTPool.spec \
    --link  BNTPool:_poolToken=PoolToken \
            BNTPool:_bnt=DummyERC20bnt \
            BNTPool:_bntGovernance=DummyTokenGovernanceA \
            BNTPool:_vbntGovernance=DummyTokenGovernanceB \
            BNTPool:_masterVault=MasterVault \
    --solc solc8.13 \
    --staging \
    --optimistic_loop \
    --packages_path node_modules \
    --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
    --msg "BNTPool no summarization"

# python3 ../../EVMVerifier/scripts/certoraRun.py  certora/munged/pools/BNTPool.sol certora/helpers/DummyERC20A.sol certora/helpers/DummyERC20B.sol \
#     certora/munged/pools/PoolToken.sol certora/munged/network/NetworkSettings.sol certora/harness/ERC20BurnableHarness.sol \
#     certora/munged/vaults/MasterVault.sol \
#     certora/helpers/DummyERC20bnt.sol \
#     certora/helpers/DummyTokenGovernanceA.sol certora/helpers/DummyTokenGovernanceB.sol \
#     --verify BNTPool:certora/spec/BNTPool.spec \
#     --link BNTPool:_poolToken=PoolToken \
#     BNTPool:_bntGovernance=DummyTokenGovernanceA \
#     BNTPool:_vbntGovernance=DummyTokenGovernanceB \
#     BNTPool:_masterVault=MasterVault \
#     BNTPool:_bnt=DummyERC20bnt \
#     --solc solc8.13 \
#     --cloud \
#     --optimistic_loop \
#     --packages_path node_modules \
#     --packages @openzeppelin=node_modules/@openzeppelin @bancor=node_modules/@bancor \
#     --msg "BNTPool new sum check"
    
    #    node_modules/@bancor/token-governance/contracts/tests/MintableToken.sol  <-- do we need this?
    #      certora/harness/OwnedHarness.sol           node_modules/@bancor/token-governance/contracts/TokenGovernance.sol