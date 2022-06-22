import {
    execute,
    grantRole,
    InstanceName,
    isLive,
    renounceRole,
    revokeRole,
    setDeploymentMetadata
} from '../../utils/Deploy';
import { Roles } from '../../utils/Roles';
import { DeployFunction } from 'hardhat-deploy/types';
import { HardhatRuntimeEnvironment } from 'hardhat/types';

const func: DeployFunction = async ({ getNamedAccounts }: HardhatRuntimeEnvironment) => {
    const { deployer, daoMultisig } = await getNamedAccounts();

    // initiate ownership transfer of the LiquidityProtection contract to the DAO
    await execute({
        name: InstanceName.LiquidityProtection,
        methodName: 'transferOwnership',
        args: [daoMultisig],
        from: deployer
    });

    // renounce the BNT ROLE_GOVERNOR role from the deployer
    await renounceRole({
        name: InstanceName.BNTGovernance,
        id: Roles.TokenGovernance.ROLE_GOVERNOR,
        from: deployer
    });

    // renounce the vBNT ROLE_GOVERNOR role from the deployer
    await renounceRole({
        name: InstanceName.VBNTGovernance,
        id: Roles.TokenGovernance.ROLE_GOVERNOR,
        from: deployer
    });

    // renounce the ROLE_EMERGENCY_STOPPER role from the deployer
    await renounceRole({
        name: InstanceName.BancorNetwork,
        id: Roles.BancorNetwork.ROLE_EMERGENCY_STOPPER,
        from: deployer
    });

    for (const name of [
        InstanceName.BancorNetworkInfo,
        InstanceName.BancorNetwork,
        InstanceName.BancorPortal,
        InstanceName.BNTPool,
        InstanceName.ExternalProtectionVault,
        InstanceName.ExternalStandardRewardsVault,
        InstanceName.MasterVault,
        InstanceName.NetworkSettings,
        InstanceName.PendingWithdrawals,
        InstanceName.PoolMigrator,
        InstanceName.PoolTokenFactory,
        InstanceName.StandardRewards
    ]) {
        await grantRole({
            name,
            id: Roles.Upgradeable.ROLE_ADMIN,
            member: daoMultisig,
            from: deployer
        });

        await revokeRole({
            name,
            id: Roles.Upgradeable.ROLE_ADMIN,
            member: deployer,
            from: deployer
        });
    }

    return true;
};

// postpone the execution of this script to the end of the beta
func.skip = async () => isLive();

export default setDeploymentMetadata(__filename, func);
