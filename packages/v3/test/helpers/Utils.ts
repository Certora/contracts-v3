import Contracts from '../../components/Contracts';
import { NetworkToken } from '../../components/LegacyContracts';
import { TestERC20Token } from '../../typechain';
import { NATIVE_TOKEN_ADDRESS } from './Constants';
import { toWei } from './Types';
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers';
import { BaseContract, BigNumber, BigNumberish, ContractTransaction, Wallet } from 'ethers';
import { ethers, waffle } from 'hardhat';

export type TokenWithAddress = TestERC20Token | { address: string };

export const toAddress = (account: string | SignerWithAddress | BaseContract) =>
    typeof account === 'string' ? account : account.address;

export const getTransactionCost = async (res: ContractTransaction) => {
    const receipt = await res.wait();
    const { cumulativeGasUsed, effectiveGasPrice } = receipt;

    return effectiveGasPrice.mul(cumulativeGasUsed);
};

export const getBalance = async (token: TokenWithAddress, account: string | SignerWithAddress) => {
    const accountAddress = toAddress(account);
    const tokenAddress = token.address;
    if (tokenAddress === NATIVE_TOKEN_ADDRESS) {
        return ethers.provider.getBalance(accountAddress);
    }
    return await (await Contracts.TestERC20Token.attach(tokenAddress)).balanceOf(accountAddress);
};

export const getBalances = async (tokens: TokenWithAddress[], account: string | SignerWithAddress) => {
    const balances: { [balance: string]: BigNumber } = {};
    for (const token of tokens) {
        balances[token.address] = await getBalance(token, account);
    }

    return balances;
};

export const transfer = async (
    sourceAccount: SignerWithAddress,
    token: TokenWithAddress,
    target: string | SignerWithAddress,
    amount: BigNumberish
) => {
    const targetAddress = toAddress(target);
    const tokenAddress = token.address;
    if (tokenAddress === NATIVE_TOKEN_ADDRESS) {
        return await sourceAccount.sendTransaction({ to: targetAddress, value: amount });
    }
    return await (await Contracts.TestERC20Token.attach(tokenAddress))
        .connect(sourceAccount)
        .transfer(targetAddress, amount);
};

export const createWallet = async () => {
    // create a random wallet, connect it to a test provider, and fund it
    const wallet = Wallet.createRandom().connect(waffle.provider);
    const deployer = (await ethers.getSigners())[0];
    await deployer.sendTransaction({
        value: toWei(BigNumber.from(10_000_000)),
        to: await wallet.getAddress()
    });

    return wallet;
};

export const createTokenBySymbol = async (
    symbol: string,
    networkToken: TestERC20Token | NetworkToken
): Promise<TokenWithAddress> => {
    switch (symbol) {
        case 'BNT':
            return networkToken as NetworkToken;

        case 'ETH':
            return { address: NATIVE_TOKEN_ADDRESS };

        case 'TKN':
        case 'TKN1':
        case 'TKN2':
            return Contracts.TestERC20Token.deploy(symbol, symbol, toWei(BigNumber.from(1_000_000_000)));

        default:
            throw new Error(`Unsupported type ${symbol}`);
    }
};

export const errorMessageTokenExceedsAllowance = (symbol: string): string => {
    switch (symbol) {
        case 'BNT':
            return '';

        case 'vBNT':
            return 'ERR_UNDERFLOW';

        case 'TKN':
        case 'TKN1':
        case 'TKN2':
            return 'ERC20: transfer amount exceeds allowance';

        default:
            throw new Error(`Unsupported type ${symbol}`);
    }
};

export const errorMessageTokenExceedsBalance = (symbol: string): string => {
    switch (symbol) {
        case 'BNT':
            return 'SafeERC20: low-level call failed';

        case 'vBNT':
            return 'ERR_UNDERFLOW';

        case 'ETH':
            return '';

        case 'TKN':
        case 'TKN1':
        case 'TKN2':
            return 'ERC20: transfer amount exceeds balance';

        default:
            throw new Error(`Unsupported type ${symbol}`);
    }
};
