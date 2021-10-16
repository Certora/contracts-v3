import { ContractBuilder, Contract } from '../../components/ContractBuilder';
import Contracts from '../../components/Contracts';
import LegacyContracts from '../../components/LegacyContracts';
import {
    BancorVault,
    NetworkSettings,
    PoolToken,
    PoolTokenFactory,
    ProxyAdmin,
    TestPoolCollection,
    TestBancorNetwork
} from '../../typechain';
import { roles } from './AccessControl';
import { DEFAULT_DECIMALS, BNT, vBNT } from './Constants';
import { toAddress, TokenWithAddress } from './Utils';
import { TokenGovernance } from '@bancor/token-governance';
import { BaseContract, BigNumber, ContractFactory } from 'ethers';
import { ethers } from 'hardhat';
import { isEqual } from 'lodash';

const { TokenGovernance: TokenGovernanceRoles, BancorVault: BancorVaultRoles } = roles;

const TOTAL_SUPPLY = BigNumber.from(1_000_000_000).mul(BigNumber.from(10).pow(18));
const V1 = 1;

type CtorArgs = Parameters<any>;
type InitArgs = Parameters<any>;

interface ProxyArguments {
    skipInitialization?: boolean;
    initArgs?: InitArgs;
    ctorArgs?: CtorArgs;
}

interface Logic {
    ctorArgs: CtorArgs;
    contract: BaseContract;
}

const logicContractsCache: Record<string, Logic> = {};
let admin: ProxyAdmin;

export const proxyAdmin = async () => {
    if (!admin) {
        admin = await Contracts.ProxyAdmin.deploy();
    }

    return admin;
};

const createLogic = async <F extends ContractFactory>(factory: ContractBuilder<F>, ctorArgs: CtorArgs = []) => {
    // check if we can reuse a previously cached exact logic contract (e.g., the same contract and constructor arguments)
    const cached = logicContractsCache[factory.metadata.contractName];
    if (cached && isEqual(cached.ctorArgs, ctorArgs)) {
        return cached.contract;
    }

    // eslint-disable-next-line @typescript-eslint/ban-types
    const logicContract = await (factory.deploy as Function)(...(ctorArgs || []));
    logicContractsCache[factory.metadata.contractName] = { ctorArgs, contract: logicContract };

    return logicContract;
};

const createTransparentProxy = async (
    logicContract: BaseContract,
    skipInitialization = false,
    initArgs: InitArgs = []
) => {
    const admin = await proxyAdmin();
    const data = skipInitialization ? [] : logicContract.interface.encodeFunctionData('initialize', initArgs);
    return Contracts.TransparentUpgradeableProxy.deploy(logicContract.address, admin.address, data);
};

const createProxy = async <F extends ContractFactory>(
    factory: ContractBuilder<F>,
    args?: ProxyArguments
): Promise<Contract<F>> => {
    const logicContract = await createLogic(factory, args?.ctorArgs);
    const proxy = await createTransparentProxy(logicContract, args?.skipInitialization, args?.initArgs);

    return factory.attach(proxy.address);
};

const createGovernedToken = async <F extends ContractFactory>(
    legacyFactory: ContractBuilder<F>,
    totalSupply: BigNumber,
    ...args: Parameters<F['deploy']>
) => {
    const deployer = (await ethers.getSigners())[0];

    const token = await legacyFactory.deploy(...args);
    await token.issue(deployer.address, totalSupply);

    const tokenGovernance = await LegacyContracts.TokenGovernance.deploy(token.address);
    await tokenGovernance.grantRole(TokenGovernanceRoles.ROLE_GOVERNOR, deployer.address);
    await tokenGovernance.grantRole(TokenGovernanceRoles.ROLE_MINTER, deployer.address);
    await token.transferOwnership(tokenGovernance.address);
    await tokenGovernance.acceptTokenOwnership();

    return { token, tokenGovernance };
};

export const createGovernedTokens = async () => {
    const { token: networkToken, tokenGovernance: networkTokenGovernance } = await createGovernedToken(
        LegacyContracts.NetworkToken,
        TOTAL_SUPPLY,
        BNT,
        BNT,
        DEFAULT_DECIMALS
    );
    const { token: govToken, tokenGovernance: govTokenGovernance } = await createGovernedToken(
        LegacyContracts.GovToken,
        TOTAL_SUPPLY,
        vBNT,
        vBNT,
        DEFAULT_DECIMALS
    );

    return { networkToken, networkTokenGovernance, govToken, govTokenGovernance };
};

export const createTokenHolder = async () => Contracts.TokenHolder.deploy();

export const createPoolCollection = async (
    network: string | BaseContract,
    poolTokenFactory: string | BaseContract,
    poolCollectionUpgrader: string | BaseContract,
    version: number = V1
) =>
    Contracts.TestPoolCollection.deploy(
        version,
        toAddress(network),
        toAddress(poolTokenFactory),
        toAddress(poolCollectionUpgrader)
    );

const createNetworkTokenPoolUninitialized = async (
    network: TestBancorNetwork,
    vault: BancorVault,
    networkPoolToken: PoolToken,
    networkTokenGovernance: TokenGovernance,
    govTokenGovernance: TokenGovernance
) => {
    const networkTokenPool = await createProxy(Contracts.TestNetworkTokenPool, {
        skipInitialization: true,
        ctorArgs: [network.address, networkPoolToken.address]
    });

    await networkPoolToken.acceptOwnership();
    await networkPoolToken.transferOwnership(networkTokenPool.address);

    await networkTokenGovernance.grantRole(TokenGovernanceRoles.ROLE_MINTER, networkTokenPool.address);
    await govTokenGovernance.grantRole(TokenGovernanceRoles.ROLE_MINTER, networkTokenPool.address);

    await vault.grantRole(BancorVaultRoles.ROLE_NETWORK_TOKEN_MANAGER, networkTokenPool.address);

    return networkTokenPool;
};

export const createPoolToken = async (poolTokenFactory: PoolTokenFactory, reserveToken: string | BaseContract) => {
    const poolTokenAddress = await poolTokenFactory.callStatic.createPoolToken(toAddress(reserveToken));

    await poolTokenFactory.createPoolToken(toAddress(reserveToken));

    return Contracts.PoolToken.attach(poolTokenAddress);
};

export const createSystem = async () => {
    const { networkToken, networkTokenGovernance, govToken, govTokenGovernance } = await createGovernedTokens();

    const networkSettings = await createProxy(Contracts.NetworkSettings);

    const vault = await createProxy(Contracts.BancorVault, { ctorArgs: [networkToken.address] });

    const poolTokenFactory = await createProxy(Contracts.PoolTokenFactory);
    const networkPoolToken = await createPoolToken(poolTokenFactory, networkToken);

    const network = await createProxy(Contracts.TestBancorNetwork, {
        skipInitialization: true,
        ctorArgs: [
            networkTokenGovernance.address,
            govTokenGovernance.address,
            networkSettings.address,
            vault.address,
            networkPoolToken.address
        ]
    });

    const pendingWithdrawals = await createProxy(Contracts.TestPendingWithdrawals, {
        ctorArgs: [network.address]
    });
    const networkTokenPool = await createNetworkTokenPoolUninitialized(
        network,
        vault,
        networkPoolToken,
        networkTokenGovernance,
        govTokenGovernance
    );

    await networkTokenPool.initialize();

    const poolCollectionUpgrader = await createProxy(Contracts.TestPoolCollectionUpgrader, {
        ctorArgs: [network.address]
    });

    const poolCollection = await createPoolCollection(network, poolTokenFactory, poolCollectionUpgrader);

    await network.initialize(networkTokenPool.address, pendingWithdrawals.address, poolCollectionUpgrader.address);

    await vault.grantRole(BancorVaultRoles.ROLE_ASSET_MANAGER, network.address);

    return {
        networkSettings,
        network,
        networkToken,
        networkTokenGovernance,
        govToken,
        govTokenGovernance,
        networkPoolToken,
        vault,
        networkTokenPool,
        pendingWithdrawals,
        poolTokenFactory,
        poolCollection,
        poolCollectionUpgrader
    };
};

export const createPool = async (
    reserveToken: TokenWithAddress,
    network: TestBancorNetwork,
    networkSettings: NetworkSettings,
    poolCollection: TestPoolCollection
) => {
    await networkSettings.addTokenToWhitelist(reserveToken.address);

    const poolCollections = await network.poolCollections();
    if (!poolCollections.includes(poolCollection.address)) {
        await network.addPoolCollection(poolCollection.address);
    }
    await network.createPool(await poolCollection.poolType(), reserveToken.address);

    const pool = await poolCollection.poolData(reserveToken.address);
    return Contracts.PoolToken.attach(pool.poolToken);
};
