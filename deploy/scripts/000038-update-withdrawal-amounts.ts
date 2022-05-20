import {
    DeployedContracts,
    execute,
    grantRole,
    InstanceName,
    setDeploymentMetadata,
    upgradeProxy
} from '../../utils/Deploy';
import { Roles } from '../../utils/Roles';
import { DeployFunction } from 'hardhat-deploy/types';
import { HardhatRuntimeEnvironment } from 'hardhat/types';

const func: DeployFunction = async ({ getNamedAccounts }: HardhatRuntimeEnvironment) => {
    const { deployer } = await getNamedAccounts();

    await grantRole({
        name: InstanceName.BancorNetwork,
        id: Roles.BancorNetwork.ROLE_EMERGENCY_STOPPER,
        member: deployer,
        from: deployer
    });

    await execute({
        name: InstanceName.BancorNetwork,
        methodName: 'pause',
        from: deployer
    });

    const network = await DeployedContracts.BancorNetwork.deployed();
    const bnt = await DeployedContracts.BNT.deployed();
    const bntPool = await DeployedContracts.BNTPool.deployed();

    await upgradeProxy({
        name: InstanceName.PendingWithdrawals,
        args: [network.address, bnt.address, bntPool.address],
        from: deployer
    });

    const bntGovernance = await DeployedContracts.BNTGovernance.deployed();
    const vbntGovernance = await DeployedContracts.VBNTGovernance.deployed();
    const networkSettings = await DeployedContracts.NetworkSettings.deployed();
    const masterVault = await DeployedContracts.MasterVault.deployed();
    const bnBNT = await DeployedContracts.bnBNT.deployed();

    await upgradeProxy({
        name: InstanceName.BNTPool,
        args: [
            network.address,
            bntGovernance.address,
            vbntGovernance.address,
            networkSettings.address,
            masterVault.address,
            bnBNT.address
        ],
        from: deployer
    });

    const externalProtectionVault = await DeployedContracts.ExternalProtectionVault.deployed();

    await upgradeProxy({
        name: InstanceName.BancorNetwork,
        args: [
            bntGovernance.address,
            vbntGovernance.address,
            networkSettings.address,
            masterVault.address,
            externalProtectionVault.address,
            bnBNT.address
        ],
        from: deployer
    });

    await execute({
        name: InstanceName.BancorNetwork,
        methodName: 'resume',
        from: deployer
    });

    return true;
};

export default setDeploymentMetadata(__filename, func);
