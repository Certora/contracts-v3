pragma solidity 0.8.13;

contract Receiver1 {
    fallback() external payable { }

    function sendTo() external payable returns (bool) { return true; }

    function sendValue() external payable returns (bool) { return true; }

    receive() external payable { }
}
