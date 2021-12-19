// SPDX-License-Identifier: MIT

pragma solidity ^0.8.2;

interface ERC20 {
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
    function totalSupply() external view returns (uint256);
    function balanceOf(address _owner) external view returns (uint256 balance);
    function transfer(address _to, uint256 _value) external returns (bool success);
    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success);
    function approve(address _spender, uint256 _value) external returns (bool success);
    function allowance(address _owner, address _spender) external view returns (uint256 remaining);

    event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
    event Transfer(address indexed from, address indexed to, uint tokens);
}

contract AmoCoin is ERC20 {
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    uint256 private _available;
    uint256 private _totalSupply;
    string private _name;
    string private _symbol;

    constructor() {
        _totalSupply = 21000000;
        _name = "AmoCoin";
        _symbol = "AMO";
    }

    function name() external view returns (string memory) { return _name; }
    function symbol() external view returns (string memory) { return _symbol; }
    function decimals() external pure returns (uint8) { return 0; }
    function totalSupply() external view returns (uint256) { return _totalSupply; }

    function balanceOf(address _owner) external view returns (uint256 balance) {
        return _balances[_owner];
    }

    function transfer(address _to, uint256 _value) external returns (bool success) {
        require(_balances[msg.sender] >= _value);

        _balances[msg.sender] -= _value;
        _balances[_to] += _value;

        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value) external returns (bool success) {
        require(_balances[_from] >= _value);
        require(_allowances[_from][msg.sender] >= _value);

        _balances[_from] -= _value;
        _balances[_to] += _value;
        _allowances[_from][msg.sender] -= _value;

        emit Transfer(_from, _to, _value);

        return true;
    }

    function approve(address _spender, uint256 _value) external returns (bool success) {
        _allowances[msg.sender][_spender] = _value;

        emit Approval(msg.sender, _spender, _value);

        return true;
    }

    function allowance(address _owner, address _spender) external view returns (uint256 remaining) {
        return _allowances[_owner][_spender];
    }

    function give(address _to, uint256 _value) external returns (bool success) {
        require(_available > 10);
        uint256 allowed = _available / 10;
        require(_value <= allowed);
        _available -= _value;
        _balances[_to] += _value;
        return true;
    }
}
