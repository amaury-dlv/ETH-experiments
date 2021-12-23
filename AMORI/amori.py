#!/usr/bin/env python3

import web3
import argparse
import itertools
from web3 import Web3
from web3.middleware import geth_poa_middleware

rinkeby_contract_addr = '0x680Bb9f1b40D89a0E74311A07A0ae01F2Cf912dE'
default_addr = '0x74D4c3647a049C9F4702F08f552F7b998d7aBBAd'

contract_addr=None

abi = [
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'name',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'},
                   {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}],
        'name': 'transfer',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'type': 'function'
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}],
        'name': 'mint',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'type': 'function'
    }
]


def balance(w3, addr):
    contract = w3.eth.contract(address=w3.toChecksumAddress(contract_addr), abi=abi)
    decimals = contract.functions.decimals().call()
    return contract.functions.balanceOf(addr).call() / 10**decimals

def info(w3, addr=None):
    contract = w3.eth.contract(address=w3.toChecksumAddress(contract_addr), abi=abi)
    name = contract.functions.name().call()
    symbol = contract.functions.symbol().call()
    decimals = contract.functions.decimals().call()
    total_supply = contract.functions.totalSupply().call() / 10**decimals

    print(f"{name} ({symbol})")
    print(f"  total_supply: {total_supply}")

    if addr:
        print(f"  balance: {balance(addr)} ({addr})")

def send_transaction(w3, from_privkey, to_addr, make_transaction):
    contract = w3.eth.contract(address=w3.toChecksumAddress(contract_addr), abi=abi)

    from_addr = w3.eth.account.privateKeyToAccount(from_privkey).address

    print(f"from: {from_addr} ({balance(w3, from_addr)})")
    print(f"  to: {to_addr} ({balance(w3, to_addr)})")
    print(f"")

    nonce = w3.eth.get_transaction_count(from_addr)

    transaction = make_transaction(contract, from_addr=from_addr)

    transaction.update({ 'gas': 2100000 })
    transaction.update({ 'nonce': nonce })

    signed_txn = w3.eth.account.sign_transaction(transaction, from_privkey)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f" txn: {txn_hash.hex()}")
    print(f"")

    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    print(f"from: {from_addr} ({balance(w3, from_addr)})")
    print(f"  to: {to_addr} ({balance(w3, to_addr)})")
    print(f"")

def transfer(w3, from_privkey, to_addr, amount):
    send_transaction(
        w3,
        from_privkey,
        to_addr,
        make_transaction=lambda contract, from_addr:
            contract.functions.transfer(to_addr, amount)
                .buildTransaction({ 'from': from_addr })
    )

def mint(w3, from_privkey, to_addr):
    send_transaction(
        w3,
        from_privkey,
        to_addr,
        make_transaction=lambda contract, from_addr:
            contract.functions.mint(to_addr).buildTransaction()
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--info", action='store_true')
    parser.add_argument("--rinkeby", action='store_true')
    parser.add_argument("--mint", action='store_true')
    parser.add_argument("--transfer", action='store_true')
    parser.add_argument("--contract", default=rinkeby_contract_addr)
    parser.add_argument("--amount", type=int)
    parser.add_argument("--addr-to", default=default_addr)
    parser.add_argument("--from-privkey")
    args = parser.parse_args()

    global contract_addr
    contract_addr = args.contract

    if args.rinkeby:
        w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/d6f3858df4d944d7bb992f931f976d22"))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        w3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))

    # https://github.com/ethereum/web3.py/issues/2145
    w3.provider.request_counter = itertools.count(start=1)

    if args.info:
        info(w3, addr=args.addr_to)
    elif args.mint:
        mint(w3, from_privkey=args.from_privkey, to_addr=args.addr_to)
    elif args.transfer:
        transfer(w3, from_privkey=args.from_privkey, to_addr=args.addr_to, amount=args.amount)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
