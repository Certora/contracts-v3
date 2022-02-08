import Contracts, {
    BancorPortal,
    NetworkSettings,
    TestBancorNetwork,
    TestPoolCollection,
    IERC20,
    BancorNetworkInfo,
    MockUniswapV2Router02,
    MockUniswapV2Pair,
    MasterPool,
    PoolToken,
    MockUniswapV2Factory
} from '../../components/Contracts';
import { TokenData, TokenSymbol, NATIVE_TOKEN_ADDRESS } from '../../utils/TokenData';
import { toWei } from '../../utils/Types';
import { createSystem, createToken, TokenWithAddress, createProxy, setupFundedPool } from '../helpers/Factory';
import { shouldHaveGap } from '../helpers/Proxy';
import { transfer, getBalances, getTransactionCost } from '../helpers/Utils';
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers';
import { expect } from 'chai';
import { BigNumber, ContractTransaction, utils } from 'ethers';
import { ethers } from 'hardhat';

const { formatBytes32String } = utils;
const FUNDING_LIMIT = toWei(10_000_000);
const CONTEXT_ID = formatBytes32String('CTX');

interface Whitelist {
    [address: string]: boolean;
}

interface AddressValueDictionary {
    [address: string]: BigNumber;
}

interface TokenAndPoolTokenBundle {
    token: TokenWithAddress;
    poolToken?: PoolToken;
}

describe.only('bancor-portal', () => {
    let network: TestBancorNetwork;
    let networkInfo: BancorNetworkInfo;
    let networkToken: IERC20;
    let masterPool: MasterPool;
    let masterPoolToken: PoolToken;
    let networkSettings: NetworkSettings;
    let poolCollection: TestPoolCollection;
    let bancorPortal: BancorPortal;
    let uniswapV2Pair: MockUniswapV2Pair;
    let uniswapV2Router02: MockUniswapV2Router02;
    let uniswapV2Factory: MockUniswapV2Factory;
    let deployer: SignerWithAddress;
    let user: SignerWithAddress;

    const amount = BigNumber.from(1000);
    const ZERO = BigNumber.from(0);

    shouldHaveGap('BancorPortal');

    before(async () => {
        [deployer, user] = await ethers.getSigners();
    });

    beforeEach(async () => {
        ({ network, networkSettings, networkToken, poolCollection, networkInfo, masterPool } = await createSystem());
        masterPoolToken = await Contracts.PoolToken.attach(await masterPool.poolToken());
        uniswapV2Pair = await Contracts.MockUniswapV2Pair.deploy(
            'UniswapV2Pair',
            'UniswapV2Pair',
            BigNumber.from(100_000_000)
        );
        uniswapV2Router02 = await Contracts.MockUniswapV2Router02.deploy(
            'UniswapV2Router02',
            'UniswapV2Router02',
            BigNumber.from(100_000_000),
            uniswapV2Pair.address
        );

        uniswapV2Factory = await Contracts.MockUniswapV2Factory.deploy(
            'UniswapV2Factory',
            'UniswapV2Factory',
            BigNumber.from(100_000_000),
            uniswapV2Pair.address
        );
        bancorPortal = await createProxy(Contracts.BancorPortal, {
            ctorArgs: [
                network.address,
                networkSettings.address,
                networkToken.address,
                uniswapV2Router02.address,
                uniswapV2Factory.address,
                uniswapV2Router02.address,
                uniswapV2Factory.address
            ]
        });

        await uniswapV2Pair.transfer(user.address, BigNumber.from(1_000_000));
    });

    describe('general', () => {
        it("reverts when none of the pair's tokens are whitelisted", async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const token0 = await createToken(new TokenData(TokenSymbol.TKN));
            const token1 = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(token0.address, token1.address);
            await uniswapV2Factory.setTokens(token0.address, token1.address);

            await expect(
                bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, 10)
            ).to.be.revertedWith('TokensNotSupported');
        });

        it('reverts if the migration is not approved', async () => {
            const token0 = await createToken(new TokenData(TokenSymbol.TKN));
            const token1 = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Factory.setTokens(token0.address, token1.address);
            await expect(
                bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, 10)
            ).to.be.revertedWith('ERC20: transfer amount exceeds allowance');
        });

        it('reverts if the input amount is 0', async () => {
            const token0 = await createToken(new TokenData(TokenSymbol.TKN));
            const token1 = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Factory.setTokens(token0.address, token1.address);
            await expect(
                bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, 0)
            ).to.be.revertedWith('ZeroValue()');
        });

        it('reverts if the input amount is less than 0', async () => {
            const token0 = await createToken(new TokenData(TokenSymbol.TKN));
            const token1 = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Factory.setTokens(token0.address, token1.address);
            await expect(bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, -1)).to.be
                .reverted;
        });

        it('reverts if there is no uniswap pair for specified tokens', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const token0 = await createToken(new TokenData(TokenSymbol.TKN));
            const token1 = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(token0.address, token1.address);
            await expect(
                bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, 10)
            ).to.be.revertedWith('NoPairForTokens()');
        });

        it('returns the correct values', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken: poolToken0, token: whitelistedToken0 } = await preparePoolAndToken(TokenSymbol.ETH);
            const { poolToken: poolToken1, token: whitelistedToken1 } = await preparePoolAndToken(TokenSymbol.TKN);
            await uniswapV2Pair.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            await uniswapV2Factory.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            const res = await testDeposit([
                { token: whitelistedToken0, poolToken: poolToken0 },
                { token: whitelistedToken1, poolToken: poolToken1 }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken0.address, whitelistedToken1.address, amount, amount);
        });
    });

    describe('transfers', () => {
        it("transfers funds to the user's wallet when only token0 is whitelisted", async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(whitelistedToken.address, unlistedToken.address);
            await uniswapV2Factory.setTokens(whitelistedToken.address, unlistedToken.address);
            await testTransfer(whitelistedToken, unlistedToken);
        });

        it("transfers funds to the user's wallet when only token1 is whitelisted", async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(unlistedToken.address, whitelistedToken.address);
            await uniswapV2Factory.setTokens(unlistedToken.address, whitelistedToken.address);
            await testTransfer(unlistedToken, whitelistedToken);
        });

        it("transfers funds to the user's wallet when token0 is eth and token1 is whitelisted", async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.ETH));
            await uniswapV2Pair.setTokens(unlistedToken.address, whitelistedToken.address);
            await uniswapV2Factory.setTokens(unlistedToken.address, whitelistedToken.address);
            await testTransfer(unlistedToken, whitelistedToken);
        });

        it("transfers funds to the user's wallet when token0 is whitelisted and token1 is eth", async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.ETH));
            await uniswapV2Pair.setTokens(whitelistedToken.address, unlistedToken.address);
            await uniswapV2Factory.setTokens(whitelistedToken.address, unlistedToken.address);
            await testTransfer(whitelistedToken, unlistedToken);
        });
    });

    describe('deposits', () => {
        it('deposits when only token0 is whitelisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Factory.setTokens(whitelistedToken.address, unlistedToken.address);
            await uniswapV2Pair.setTokens(whitelistedToken.address, unlistedToken.address);
            const res = await testDeposit([{ token: whitelistedToken, poolToken }, { token: unlistedToken }]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken.address, unlistedToken.address, amount, ZERO);
        });

        it('deposits when only token1 is whitelisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(unlistedToken.address, whitelistedToken.address);
            await uniswapV2Factory.setTokens(unlistedToken.address, whitelistedToken.address);
            const res = await testDeposit([{ token: unlistedToken }, { token: whitelistedToken, poolToken }]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, unlistedToken.address, whitelistedToken.address, ZERO, amount);
        });

        it('deposits both tokens when possible', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken: poolToken0, token: token0 } = await preparePoolAndToken(TokenSymbol.TKN);
            const { poolToken: poolToken1, token: token1 } = await preparePoolAndToken(TokenSymbol.TKN1);
            await uniswapV2Pair.setTokens(token0.address, token1.address);
            await uniswapV2Factory.setTokens(token0.address, token1.address);
            const res = await testDeposit([
                { token: token0, poolToken: poolToken0 },
                { token: token1, poolToken: poolToken1 }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, token0.address, token1.address, amount, amount);
        });

        it('deposits when token0 is eth and token1 is unlisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.ETH);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(whitelistedToken.address, unlistedToken.address);
            await uniswapV2Factory.setTokens(whitelistedToken.address, unlistedToken.address);
            const res = await testDeposit([{ token: whitelistedToken, poolToken }, { token: unlistedToken }]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken.address, unlistedToken.address, amount, ZERO);
        });

        it('deposits when token0 is eth and token1 is whitelisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken: poolToken0, token: whitelistedToken0 } = await preparePoolAndToken(TokenSymbol.ETH);
            const { poolToken: poolToken1, token: whitelistedToken1 } = await preparePoolAndToken(TokenSymbol.TKN);
            await uniswapV2Pair.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            await uniswapV2Factory.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            const res = await testDeposit([
                { token: whitelistedToken0, poolToken: poolToken0 },
                { token: whitelistedToken1, poolToken: poolToken1 }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken0.address, whitelistedToken1.address, amount, amount);
        });

        it('deposits when token0 is unlisted and token1 is eth', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.ETH);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(unlistedToken.address, whitelistedToken.address);
            await uniswapV2Factory.setTokens(unlistedToken.address, whitelistedToken.address);
            const res = await testDeposit([{ token: unlistedToken }, { token: whitelistedToken, poolToken }]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, unlistedToken.address, whitelistedToken.address, ZERO, amount);
        });

        it('deposits when token0 is whitelisted and token1 is eth', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken: poolToken0, token: whitelistedToken0 } = await preparePoolAndToken(TokenSymbol.TKN);
            const { poolToken: poolToken1, token: whitelistedToken1 } = await preparePoolAndToken(TokenSymbol.ETH);
            await uniswapV2Pair.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            await uniswapV2Factory.setTokens(whitelistedToken0.address, whitelistedToken1.address);
            const res = await testDeposit([
                { token: whitelistedToken0, poolToken: poolToken0 },
                { token: whitelistedToken1, poolToken: poolToken1 }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken0.address, whitelistedToken1.address, amount, amount);
        });

        it('deposits when token0 is bnt and token1 is unlisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            await networkSettings.setFundingLimit(whitelistedToken.address, FUNDING_LIMIT);
            await poolCollection.requestFundingT(CONTEXT_ID, whitelistedToken.address, amount);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(networkToken.address, unlistedToken.address);
            await uniswapV2Factory.setTokens(networkToken.address, unlistedToken.address);
            const res = await testDeposit([
                { token: networkToken, poolToken: masterPoolToken },
                { token: unlistedToken }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, networkToken.address, unlistedToken.address, amount, ZERO);
        });

        it('deposits when token0 is unlisted and token1 is bnt', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            await networkSettings.setFundingLimit(whitelistedToken.address, FUNDING_LIMIT);
            await poolCollection.requestFundingT(CONTEXT_ID, whitelistedToken.address, amount);
            const unlistedToken = await createToken(new TokenData(TokenSymbol.TKN1));
            await uniswapV2Pair.setTokens(unlistedToken.address, networkToken.address);
            await uniswapV2Factory.setTokens(unlistedToken.address, networkToken.address);
            const res = await testDeposit([
                { token: unlistedToken },
                { token: networkToken, poolToken: masterPoolToken }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, unlistedToken.address, networkToken.address, ZERO, amount);
        });

        it('deposits when token0 is bnt and token1 is whitelisted', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            await networkSettings.setFundingLimit(whitelistedToken.address, FUNDING_LIMIT);
            await poolCollection.requestFundingT(CONTEXT_ID, whitelistedToken.address, amount);
            await uniswapV2Pair.setTokens(networkToken.address, whitelistedToken.address);
            await uniswapV2Factory.setTokens(networkToken.address, whitelistedToken.address);
            const res = await testDeposit([
                { token: networkToken, poolToken: masterPoolToken },
                { token: whitelistedToken, poolToken }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, networkToken.address, whitelistedToken.address, amount, amount);
        });

        it('deposits when token0 is whitelisted and token1 is bnt', async () => {
            await uniswapV2Pair.connect(user).approve(bancorPortal.address, amount);
            const { poolToken, token: whitelistedToken } = await preparePoolAndToken(TokenSymbol.TKN);
            await networkSettings.setFundingLimit(whitelistedToken.address, FUNDING_LIMIT);
            await poolCollection.requestFundingT(CONTEXT_ID, whitelistedToken.address, amount);
            await uniswapV2Pair.setTokens(whitelistedToken.address, networkToken.address);
            await uniswapV2Factory.setTokens(whitelistedToken.address, networkToken.address);
            const res = await testDeposit([
                { token: whitelistedToken, poolToken },
                { token: networkToken, poolToken: masterPoolToken }
            ]);
            expect(res)
                .to.emit(bancorPortal, 'UniswapV2PositionMigrated')
                .withArgs(user.address, whitelistedToken.address, networkToken.address, amount, amount);
        });
    });

    /**
     * reusable transfer test, pass different combinations of tokens to test a specific scenario
     * @param token0 whitelisted, unlisted, native or network
     * @param token1 whitelisted, unlisted, native or network
     */
    const testTransfer = async (token0: TokenWithAddress, token1: TokenWithAddress) => {
        // prepare uniswap mocks
        await transfer(deployer, token0, uniswapV2Pair.address, amount);
        await transfer(deployer, token1, uniswapV2Pair.address, amount);
        deployer.sendTransaction({ to: uniswapV2Pair.address, value: amount });

        // save state
        const previousBalances = await getBalances([token0, token1], user);

        // execute
        const res = await bancorPortal.connect(user).migrateUniswapV2Position(token0.address, token1.address, amount);

        // assert
        const newBalances = await getBalances([token0, token1], user);
        const whitelist = await getWhitelist(token0.address, token1.address);
        if (whitelist[token0.address] && whitelist[token1.address]) {
            expect(newBalances[token0.address].eq(previousBalances[token0.address].add(amount))).to.be.true;
            expect(newBalances[token1.address].eq(previousBalances[token1.address].add(amount))).to.be.true;
        } else {
            if (whitelist[token0.address]) {
                const transactionCost = isNativeToken(token1) ? await getTransactionCost(res) : 0;
                expect(newBalances[token0.address].eq(previousBalances[token0.address])).to.be.true;
                expect(
                    newBalances[token1.address].eq(previousBalances[token1.address].add(amount).sub(transactionCost))
                ).to.be.true;
            } else {
                const transactionCost = isNativeToken(token0) ? await getTransactionCost(res) : 0;
                expect(
                    newBalances[token0.address].eq(previousBalances[token0.address].add(amount).sub(transactionCost))
                ).to.be.true;
                expect(newBalances[token1.address].eq(previousBalances[token1.address])).to.be.true;
            }
        }
        console.log(previousBalances, newBalances);
    };

    /**
     * reusable deposit test, pass different combinations of tokens to test a specific scenario
     * @param bundles array of whitelisted, unlisted, native or network tokens, and their associated poolTokens
     */
    const testDeposit = async (bundles: Array<TokenAndPoolTokenBundle>): Promise<ContractTransaction> => {
        // fund uniswap mock
        await transfer(deployer, bundles[0].token, uniswapV2Pair.address, amount);
        await transfer(deployer, bundles[1].token, uniswapV2Pair.address, amount);

        // save state
        const previousStakedBalances = await getStakedBalances(bundles[0].token, bundles[1].token);
        const previousPoolTokenBalances = await getPoolTokenBalances(bundles[0].poolToken, bundles[1].poolToken);
        const whitelist = await getWhitelist(bundles[0].token.address, bundles[1].token.address);

        // execute
        const res = await bancorPortal
            .connect(user)
            .migrateUniswapV2Position(bundles[0].token.address, bundles[1].token.address, amount);
        const newStakedBalances = await getStakedBalances(bundles[0].token, bundles[1].token);
        const newPoolTokenBalances = await getPoolTokenBalances(bundles[0].poolToken, bundles[1].poolToken);

        // assert staked balances
        for (const t of bundles.map((b) => b.token)) {
            if (isNetworkToken(t)) continue;

            if (whitelist[t.address]) {
                expect(newStakedBalances[t.address]).to.equal(previousStakedBalances[t.address].add(amount));
            } else {
                expect(newStakedBalances[t.address]).to.equal(previousStakedBalances[t.address]);
            }
        }

        // assert poolToken balances
        for (const bundle of bundles) {
            if (bundle.poolToken && whitelist[bundle.token.address]) {
                expect(newPoolTokenBalances[bundle.poolToken.address]).to.equal(
                    previousPoolTokenBalances[bundle.poolToken.address].add(amount)
                );
            }
        }

        return res;
    };

    /**
     * get balance of [poolToken0] and [poolToken1]
     * @param poolToken0
     * @param poolToken1
     * @returns
     */
    const getPoolTokenBalances = async (
        poolToken0?: PoolToken,
        poolToken1?: PoolToken
    ): Promise<AddressValueDictionary> => {
        const balances: AddressValueDictionary = {};
        for (const t of [poolToken0, poolToken1]) {
            if (t) {
                balances[t.address] = await t.balanceOf(user.address);
            }
        }
        return balances;
    };

    const getStakedBalances = async (
        token0: TokenWithAddress,
        token1: TokenWithAddress
    ): Promise<AddressValueDictionary> => {
        const balances: { [address: string]: BigNumber } = {};
        for (const t of [token0, token1]) {
            if (isNetworkToken(t)) continue;

            balances[t.address] = (await poolCollection.poolData(t.address)).liquidity[2];
        }
        return balances;
    };

    /**
     * get whitelist status of [token0] and [token1], return true networkToken.
     * @param token0 token or networkToken
     * @param token1 token or networkToken
     * @returns dictioary [address: booleann]
     */
    const getWhitelist = async (token0: string, token1: string): Promise<Whitelist> => {
        const whitelist: Whitelist = {};
        whitelist[token0] = token0 === networkToken.address ? true : await networkSettings.isTokenWhitelisted(token0);
        whitelist[token1] = token1 === networkToken.address ? true : await networkSettings.isTokenWhitelisted(token1);
        return whitelist;
    };

    /**
     * prepare, configure and fund a pool for given [symbol]
     * @param symbol
     * @returns newly created poolToken and token
     */
    const preparePoolAndToken = async (symbol: TokenSymbol) => {
        const balance = toWei(100_000_000);
        const { poolToken, token } = await setupFundedPool(
            {
                tokenData: new TokenData(symbol),
                balance: balance,
                requestedLiquidity: balance.mul(1000),
                fundingRate: { n: 1, d: 2 }
            },
            deployer as any as SignerWithAddress,
            network,
            networkInfo,
            networkSettings,
            poolCollection
        );

        return { poolToken, token };
    };

    const isNativeToken = (token: TokenWithAddress): boolean => {
        return token.address === NATIVE_TOKEN_ADDRESS;
    };

    const isNetworkToken = (token: TokenWithAddress): boolean => {
        return token.address === networkToken.address;
    };
});
