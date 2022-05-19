/* Autogenerated file. Do not edit manually. */

/* tslint:disable */

/* eslint-disable */
import type {
  TypedEventFilter,
  TypedEvent,
  TypedListener,
  OnEvent,
} from "../../common";
import type {
  FunctionFragment,
  Result,
  EventFragment,
} from "@ethersproject/abi";
import type { Listener, Provider } from "@ethersproject/providers";
import type {
  BaseContract,
  BigNumber,
  BigNumberish,
  BytesLike,
  CallOverrides,
  ContractTransaction,
  Overrides,
  PopulatedTransaction,
  Signer,
  utils,
} from "ethers";

export type CompletedWithdrawalStruct = {
  poolToken: string;
  poolTokenAmount: BigNumberish;
};

export type CompletedWithdrawalStructOutput = [string, BigNumber] & {
  poolToken: string;
  poolTokenAmount: BigNumber;
};

export type WithdrawalRequestStruct = {
  provider: string;
  poolToken: string;
  reserveToken: string;
  createdAt: BigNumberish;
  poolTokenAmount: BigNumberish;
  reserveTokenAmount: BigNumberish;
};

export type WithdrawalRequestStructOutput = [
  string,
  string,
  string,
  number,
  BigNumber,
  BigNumber
] & {
  provider: string;
  poolToken: string;
  reserveToken: string;
  createdAt: number;
  poolTokenAmount: BigNumber;
  reserveTokenAmount: BigNumber;
};

export interface PendingWithdrawalsInterface extends utils.Interface {
  functions: {
    "DEFAULT_ADMIN_ROLE()": FunctionFragment;
    "cancelWithdrawal(address,uint256)": FunctionFragment;
    "completeWithdrawal(bytes32,address,uint256)": FunctionFragment;
    "getRoleAdmin(bytes32)": FunctionFragment;
    "getRoleMember(bytes32,uint256)": FunctionFragment;
    "getRoleMemberCount(bytes32)": FunctionFragment;
    "grantRole(bytes32,address)": FunctionFragment;
    "hasRole(bytes32,address)": FunctionFragment;
    "initWithdrawal(address,address,uint256)": FunctionFragment;
    "initialize()": FunctionFragment;
    "isReadyForWithdrawal(uint256)": FunctionFragment;
    "lockDuration()": FunctionFragment;
    "postUpgrade(bytes)": FunctionFragment;
    "renounceRole(bytes32,address)": FunctionFragment;
    "revokeRole(bytes32,address)": FunctionFragment;
    "roleAdmin()": FunctionFragment;
    "setLockDuration(uint32)": FunctionFragment;
    "supportsInterface(bytes4)": FunctionFragment;
    "version()": FunctionFragment;
    "withdrawalRequest(uint256)": FunctionFragment;
    "withdrawalRequestCount(address)": FunctionFragment;
    "withdrawalRequestIds(address)": FunctionFragment;
  };

  getFunction(
    nameOrSignatureOrTopic:
      | "DEFAULT_ADMIN_ROLE"
      | "cancelWithdrawal"
      | "completeWithdrawal"
      | "getRoleAdmin"
      | "getRoleMember"
      | "getRoleMemberCount"
      | "grantRole"
      | "hasRole"
      | "initWithdrawal"
      | "initialize"
      | "isReadyForWithdrawal"
      | "lockDuration"
      | "postUpgrade"
      | "renounceRole"
      | "revokeRole"
      | "roleAdmin"
      | "setLockDuration"
      | "supportsInterface"
      | "version"
      | "withdrawalRequest"
      | "withdrawalRequestCount"
      | "withdrawalRequestIds"
  ): FunctionFragment;

  encodeFunctionData(
    functionFragment: "DEFAULT_ADMIN_ROLE",
    values?: undefined
  ): string;
  encodeFunctionData(
    functionFragment: "cancelWithdrawal",
    values: [string, BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "completeWithdrawal",
    values: [BytesLike, string, BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "getRoleAdmin",
    values: [BytesLike]
  ): string;
  encodeFunctionData(
    functionFragment: "getRoleMember",
    values: [BytesLike, BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "getRoleMemberCount",
    values: [BytesLike]
  ): string;
  encodeFunctionData(
    functionFragment: "grantRole",
    values: [BytesLike, string]
  ): string;
  encodeFunctionData(
    functionFragment: "hasRole",
    values: [BytesLike, string]
  ): string;
  encodeFunctionData(
    functionFragment: "initWithdrawal",
    values: [string, string, BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "initialize",
    values?: undefined
  ): string;
  encodeFunctionData(
    functionFragment: "isReadyForWithdrawal",
    values: [BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "lockDuration",
    values?: undefined
  ): string;
  encodeFunctionData(
    functionFragment: "postUpgrade",
    values: [BytesLike]
  ): string;
  encodeFunctionData(
    functionFragment: "renounceRole",
    values: [BytesLike, string]
  ): string;
  encodeFunctionData(
    functionFragment: "revokeRole",
    values: [BytesLike, string]
  ): string;
  encodeFunctionData(functionFragment: "roleAdmin", values?: undefined): string;
  encodeFunctionData(
    functionFragment: "setLockDuration",
    values: [BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "supportsInterface",
    values: [BytesLike]
  ): string;
  encodeFunctionData(functionFragment: "version", values?: undefined): string;
  encodeFunctionData(
    functionFragment: "withdrawalRequest",
    values: [BigNumberish]
  ): string;
  encodeFunctionData(
    functionFragment: "withdrawalRequestCount",
    values: [string]
  ): string;
  encodeFunctionData(
    functionFragment: "withdrawalRequestIds",
    values: [string]
  ): string;

  decodeFunctionResult(
    functionFragment: "DEFAULT_ADMIN_ROLE",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "cancelWithdrawal",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "completeWithdrawal",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "getRoleAdmin",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "getRoleMember",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "getRoleMemberCount",
    data: BytesLike
  ): Result;
  decodeFunctionResult(functionFragment: "grantRole", data: BytesLike): Result;
  decodeFunctionResult(functionFragment: "hasRole", data: BytesLike): Result;
  decodeFunctionResult(
    functionFragment: "initWithdrawal",
    data: BytesLike
  ): Result;
  decodeFunctionResult(functionFragment: "initialize", data: BytesLike): Result;
  decodeFunctionResult(
    functionFragment: "isReadyForWithdrawal",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "lockDuration",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "postUpgrade",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "renounceRole",
    data: BytesLike
  ): Result;
  decodeFunctionResult(functionFragment: "revokeRole", data: BytesLike): Result;
  decodeFunctionResult(functionFragment: "roleAdmin", data: BytesLike): Result;
  decodeFunctionResult(
    functionFragment: "setLockDuration",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "supportsInterface",
    data: BytesLike
  ): Result;
  decodeFunctionResult(functionFragment: "version", data: BytesLike): Result;
  decodeFunctionResult(
    functionFragment: "withdrawalRequest",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "withdrawalRequestCount",
    data: BytesLike
  ): Result;
  decodeFunctionResult(
    functionFragment: "withdrawalRequestIds",
    data: BytesLike
  ): Result;

  events: {
    "LockDurationUpdated(uint32,uint32)": EventFragment;
    "RoleAdminChanged(bytes32,bytes32,bytes32)": EventFragment;
    "RoleGranted(bytes32,address,address)": EventFragment;
    "RoleRevoked(bytes32,address,address)": EventFragment;
    "WithdrawalCancelled(address,address,uint256,uint256,uint256,uint32)": EventFragment;
    "WithdrawalCompleted(bytes32,address,address,uint256,uint256,uint256,uint32)": EventFragment;
    "WithdrawalInitiated(address,address,uint256,uint256,uint256)": EventFragment;
  };

  getEvent(nameOrSignatureOrTopic: "LockDurationUpdated"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "RoleAdminChanged"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "RoleGranted"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "RoleRevoked"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "WithdrawalCancelled"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "WithdrawalCompleted"): EventFragment;
  getEvent(nameOrSignatureOrTopic: "WithdrawalInitiated"): EventFragment;
}

export interface LockDurationUpdatedEventObject {
  prevLockDuration: number;
  newLockDuration: number;
}
export type LockDurationUpdatedEvent = TypedEvent<
  [number, number],
  LockDurationUpdatedEventObject
>;

export type LockDurationUpdatedEventFilter =
  TypedEventFilter<LockDurationUpdatedEvent>;

export interface RoleAdminChangedEventObject {
  role: string;
  previousAdminRole: string;
  newAdminRole: string;
}
export type RoleAdminChangedEvent = TypedEvent<
  [string, string, string],
  RoleAdminChangedEventObject
>;

export type RoleAdminChangedEventFilter =
  TypedEventFilter<RoleAdminChangedEvent>;

export interface RoleGrantedEventObject {
  role: string;
  account: string;
  sender: string;
}
export type RoleGrantedEvent = TypedEvent<
  [string, string, string],
  RoleGrantedEventObject
>;

export type RoleGrantedEventFilter = TypedEventFilter<RoleGrantedEvent>;

export interface RoleRevokedEventObject {
  role: string;
  account: string;
  sender: string;
}
export type RoleRevokedEvent = TypedEvent<
  [string, string, string],
  RoleRevokedEventObject
>;

export type RoleRevokedEventFilter = TypedEventFilter<RoleRevokedEvent>;

export interface WithdrawalCancelledEventObject {
  pool: string;
  provider: string;
  requestId: BigNumber;
  poolTokenAmount: BigNumber;
  reserveTokenAmount: BigNumber;
  timeElapsed: number;
}
export type WithdrawalCancelledEvent = TypedEvent<
  [string, string, BigNumber, BigNumber, BigNumber, number],
  WithdrawalCancelledEventObject
>;

export type WithdrawalCancelledEventFilter =
  TypedEventFilter<WithdrawalCancelledEvent>;

export interface WithdrawalCompletedEventObject {
  contextId: string;
  pool: string;
  provider: string;
  requestId: BigNumber;
  poolTokenAmount: BigNumber;
  reserveTokenAmount: BigNumber;
  timeElapsed: number;
}
export type WithdrawalCompletedEvent = TypedEvent<
  [string, string, string, BigNumber, BigNumber, BigNumber, number],
  WithdrawalCompletedEventObject
>;

export type WithdrawalCompletedEventFilter =
  TypedEventFilter<WithdrawalCompletedEvent>;

export interface WithdrawalInitiatedEventObject {
  pool: string;
  provider: string;
  requestId: BigNumber;
  poolTokenAmount: BigNumber;
  reserveTokenAmount: BigNumber;
}
export type WithdrawalInitiatedEvent = TypedEvent<
  [string, string, BigNumber, BigNumber, BigNumber],
  WithdrawalInitiatedEventObject
>;

export type WithdrawalInitiatedEventFilter =
  TypedEventFilter<WithdrawalInitiatedEvent>;

export interface PendingWithdrawals extends BaseContract {
  connect(signerOrProvider: Signer | Provider | string): this;
  attach(addressOrName: string): this;
  deployed(): Promise<this>;

  interface: PendingWithdrawalsInterface;

  queryFilter<TEvent extends TypedEvent>(
    event: TypedEventFilter<TEvent>,
    fromBlockOrBlockhash?: string | number | undefined,
    toBlock?: string | number | undefined
  ): Promise<Array<TEvent>>;

  listeners<TEvent extends TypedEvent>(
    eventFilter?: TypedEventFilter<TEvent>
  ): Array<TypedListener<TEvent>>;
  listeners(eventName?: string): Array<Listener>;
  removeAllListeners<TEvent extends TypedEvent>(
    eventFilter: TypedEventFilter<TEvent>
  ): this;
  removeAllListeners(eventName?: string): this;
  off: OnEvent<this>;
  on: OnEvent<this>;
  once: OnEvent<this>;
  removeListener: OnEvent<this>;

  functions: {
    DEFAULT_ADMIN_ROLE(overrides?: CallOverrides): Promise<[string]>;

    cancelWithdrawal(
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    completeWithdrawal(
      contextId: BytesLike,
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    getRoleAdmin(role: BytesLike, overrides?: CallOverrides): Promise<[string]>;

    getRoleMember(
      role: BytesLike,
      index: BigNumberish,
      overrides?: CallOverrides
    ): Promise<[string]>;

    getRoleMemberCount(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<[BigNumber]>;

    grantRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    hasRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<[boolean]>;

    initWithdrawal(
      provider: string,
      poolToken: string,
      poolTokenAmount: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    initialize(
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    isReadyForWithdrawal(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<[boolean]>;

    lockDuration(overrides?: CallOverrides): Promise<[number]>;

    postUpgrade(
      data: BytesLike,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    renounceRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    revokeRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    roleAdmin(overrides?: CallOverrides): Promise<[string]>;

    setLockDuration(
      newLockDuration: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<ContractTransaction>;

    supportsInterface(
      interfaceId: BytesLike,
      overrides?: CallOverrides
    ): Promise<[boolean]>;

    version(overrides?: CallOverrides): Promise<[number]>;

    withdrawalRequest(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<[WithdrawalRequestStructOutput]>;

    withdrawalRequestCount(
      provider: string,
      overrides?: CallOverrides
    ): Promise<[BigNumber]>;

    withdrawalRequestIds(
      provider: string,
      overrides?: CallOverrides
    ): Promise<[BigNumber[]]>;
  };

  DEFAULT_ADMIN_ROLE(overrides?: CallOverrides): Promise<string>;

  cancelWithdrawal(
    provider: string,
    id: BigNumberish,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  completeWithdrawal(
    contextId: BytesLike,
    provider: string,
    id: BigNumberish,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  getRoleAdmin(role: BytesLike, overrides?: CallOverrides): Promise<string>;

  getRoleMember(
    role: BytesLike,
    index: BigNumberish,
    overrides?: CallOverrides
  ): Promise<string>;

  getRoleMemberCount(
    role: BytesLike,
    overrides?: CallOverrides
  ): Promise<BigNumber>;

  grantRole(
    role: BytesLike,
    account: string,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  hasRole(
    role: BytesLike,
    account: string,
    overrides?: CallOverrides
  ): Promise<boolean>;

  initWithdrawal(
    provider: string,
    poolToken: string,
    poolTokenAmount: BigNumberish,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  initialize(
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  isReadyForWithdrawal(
    id: BigNumberish,
    overrides?: CallOverrides
  ): Promise<boolean>;

  lockDuration(overrides?: CallOverrides): Promise<number>;

  postUpgrade(
    data: BytesLike,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  renounceRole(
    role: BytesLike,
    account: string,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  revokeRole(
    role: BytesLike,
    account: string,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  roleAdmin(overrides?: CallOverrides): Promise<string>;

  setLockDuration(
    newLockDuration: BigNumberish,
    overrides?: Overrides & { from?: string | Promise<string> }
  ): Promise<ContractTransaction>;

  supportsInterface(
    interfaceId: BytesLike,
    overrides?: CallOverrides
  ): Promise<boolean>;

  version(overrides?: CallOverrides): Promise<number>;

  withdrawalRequest(
    id: BigNumberish,
    overrides?: CallOverrides
  ): Promise<WithdrawalRequestStructOutput>;

  withdrawalRequestCount(
    provider: string,
    overrides?: CallOverrides
  ): Promise<BigNumber>;

  withdrawalRequestIds(
    provider: string,
    overrides?: CallOverrides
  ): Promise<BigNumber[]>;

  callStatic: {
    DEFAULT_ADMIN_ROLE(overrides?: CallOverrides): Promise<string>;

    cancelWithdrawal(
      provider: string,
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    completeWithdrawal(
      contextId: BytesLike,
      provider: string,
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<CompletedWithdrawalStructOutput>;

    getRoleAdmin(role: BytesLike, overrides?: CallOverrides): Promise<string>;

    getRoleMember(
      role: BytesLike,
      index: BigNumberish,
      overrides?: CallOverrides
    ): Promise<string>;

    getRoleMemberCount(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    grantRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<void>;

    hasRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<boolean>;

    initWithdrawal(
      provider: string,
      poolToken: string,
      poolTokenAmount: BigNumberish,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    initialize(overrides?: CallOverrides): Promise<void>;

    isReadyForWithdrawal(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<boolean>;

    lockDuration(overrides?: CallOverrides): Promise<number>;

    postUpgrade(data: BytesLike, overrides?: CallOverrides): Promise<void>;

    renounceRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<void>;

    revokeRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<void>;

    roleAdmin(overrides?: CallOverrides): Promise<string>;

    setLockDuration(
      newLockDuration: BigNumberish,
      overrides?: CallOverrides
    ): Promise<void>;

    supportsInterface(
      interfaceId: BytesLike,
      overrides?: CallOverrides
    ): Promise<boolean>;

    version(overrides?: CallOverrides): Promise<number>;

    withdrawalRequest(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<WithdrawalRequestStructOutput>;

    withdrawalRequestCount(
      provider: string,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    withdrawalRequestIds(
      provider: string,
      overrides?: CallOverrides
    ): Promise<BigNumber[]>;
  };

  filters: {
    "LockDurationUpdated(uint32,uint32)"(
      prevLockDuration?: null,
      newLockDuration?: null
    ): LockDurationUpdatedEventFilter;
    LockDurationUpdated(
      prevLockDuration?: null,
      newLockDuration?: null
    ): LockDurationUpdatedEventFilter;

    "RoleAdminChanged(bytes32,bytes32,bytes32)"(
      role?: BytesLike | null,
      previousAdminRole?: BytesLike | null,
      newAdminRole?: BytesLike | null
    ): RoleAdminChangedEventFilter;
    RoleAdminChanged(
      role?: BytesLike | null,
      previousAdminRole?: BytesLike | null,
      newAdminRole?: BytesLike | null
    ): RoleAdminChangedEventFilter;

    "RoleGranted(bytes32,address,address)"(
      role?: BytesLike | null,
      account?: string | null,
      sender?: string | null
    ): RoleGrantedEventFilter;
    RoleGranted(
      role?: BytesLike | null,
      account?: string | null,
      sender?: string | null
    ): RoleGrantedEventFilter;

    "RoleRevoked(bytes32,address,address)"(
      role?: BytesLike | null,
      account?: string | null,
      sender?: string | null
    ): RoleRevokedEventFilter;
    RoleRevoked(
      role?: BytesLike | null,
      account?: string | null,
      sender?: string | null
    ): RoleRevokedEventFilter;

    "WithdrawalCancelled(address,address,uint256,uint256,uint256,uint32)"(
      pool?: string | null,
      provider?: string | null,
      requestId?: BigNumberish | null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null,
      timeElapsed?: null
    ): WithdrawalCancelledEventFilter;
    WithdrawalCancelled(
      pool?: string | null,
      provider?: string | null,
      requestId?: BigNumberish | null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null,
      timeElapsed?: null
    ): WithdrawalCancelledEventFilter;

    "WithdrawalCompleted(bytes32,address,address,uint256,uint256,uint256,uint32)"(
      contextId?: BytesLike | null,
      pool?: string | null,
      provider?: string | null,
      requestId?: null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null,
      timeElapsed?: null
    ): WithdrawalCompletedEventFilter;
    WithdrawalCompleted(
      contextId?: BytesLike | null,
      pool?: string | null,
      provider?: string | null,
      requestId?: null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null,
      timeElapsed?: null
    ): WithdrawalCompletedEventFilter;

    "WithdrawalInitiated(address,address,uint256,uint256,uint256)"(
      pool?: string | null,
      provider?: string | null,
      requestId?: BigNumberish | null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null
    ): WithdrawalInitiatedEventFilter;
    WithdrawalInitiated(
      pool?: string | null,
      provider?: string | null,
      requestId?: BigNumberish | null,
      poolTokenAmount?: null,
      reserveTokenAmount?: null
    ): WithdrawalInitiatedEventFilter;
  };

  estimateGas: {
    DEFAULT_ADMIN_ROLE(overrides?: CallOverrides): Promise<BigNumber>;

    cancelWithdrawal(
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    completeWithdrawal(
      contextId: BytesLike,
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    getRoleAdmin(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    getRoleMember(
      role: BytesLike,
      index: BigNumberish,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    getRoleMemberCount(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    grantRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    hasRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    initWithdrawal(
      provider: string,
      poolToken: string,
      poolTokenAmount: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    initialize(
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    isReadyForWithdrawal(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    lockDuration(overrides?: CallOverrides): Promise<BigNumber>;

    postUpgrade(
      data: BytesLike,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    renounceRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    revokeRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    roleAdmin(overrides?: CallOverrides): Promise<BigNumber>;

    setLockDuration(
      newLockDuration: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<BigNumber>;

    supportsInterface(
      interfaceId: BytesLike,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    version(overrides?: CallOverrides): Promise<BigNumber>;

    withdrawalRequest(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    withdrawalRequestCount(
      provider: string,
      overrides?: CallOverrides
    ): Promise<BigNumber>;

    withdrawalRequestIds(
      provider: string,
      overrides?: CallOverrides
    ): Promise<BigNumber>;
  };

  populateTransaction: {
    DEFAULT_ADMIN_ROLE(
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    cancelWithdrawal(
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    completeWithdrawal(
      contextId: BytesLike,
      provider: string,
      id: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    getRoleAdmin(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    getRoleMember(
      role: BytesLike,
      index: BigNumberish,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    getRoleMemberCount(
      role: BytesLike,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    grantRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    hasRole(
      role: BytesLike,
      account: string,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    initWithdrawal(
      provider: string,
      poolToken: string,
      poolTokenAmount: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    initialize(
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    isReadyForWithdrawal(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    lockDuration(overrides?: CallOverrides): Promise<PopulatedTransaction>;

    postUpgrade(
      data: BytesLike,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    renounceRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    revokeRole(
      role: BytesLike,
      account: string,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    roleAdmin(overrides?: CallOverrides): Promise<PopulatedTransaction>;

    setLockDuration(
      newLockDuration: BigNumberish,
      overrides?: Overrides & { from?: string | Promise<string> }
    ): Promise<PopulatedTransaction>;

    supportsInterface(
      interfaceId: BytesLike,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    version(overrides?: CallOverrides): Promise<PopulatedTransaction>;

    withdrawalRequest(
      id: BigNumberish,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    withdrawalRequestCount(
      provider: string,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;

    withdrawalRequestIds(
      provider: string,
      overrides?: CallOverrides
    ): Promise<PopulatedTransaction>;
  };
}
