// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.13;

// with mint
contract DummyERC20Impl {
    uint256 t;
    mapping (address => uint256) b;
    mapping (address => mapping (address => uint256)) a;

    string public name;
    string public symbol;
    uint public decimals;

    // Function can be set as view.
    function myAddress() public view returns (address) {
        return address(this);
    }
    // (a,b) -> (x,y) (Not an error, but for clarity)
    function add(uint x, uint y) internal pure returns (uint256) {
        uint z = x+y;
        require (z >= x);
        return z;
    }
    // (a,b) -> (x,y) (Not an error, but for clarity)
    function sub(uint x, uint y) internal pure returns (uint256) {
        require (x>=y);
        return x-y;
    }

    function totalSupply() external view returns (uint256) {
        return t;
    }
    function balanceOf(address account) external view returns (uint256) {
        return b[account];
    }
    function transfer(address recipient, uint256 amount) external returns (bool) {
        b[msg.sender] = sub(b[msg.sender], amount);
        b[recipient] = add(b[recipient], amount);
        return true;
    }
    function allowance(address owner, address spender) external view returns (uint256) {
        return a[owner][spender];
    }
    function approve(address spender, uint256 amount) external returns (bool) {
        a[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool) {
        b[sender] = sub(b[sender], amount);
        b[recipient] = add(b[recipient], amount);
        a[sender][msg.sender] = sub(a[sender][msg.sender], amount);
        return true;
    }
}
