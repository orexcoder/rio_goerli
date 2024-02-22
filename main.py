import time

from web3 import Web3
from termcolor import cprint
import random
from config import time_sleep_from, time_sleep_to, deposite_eth_from, deposite_eth_to, iterations_from, iterations_to, withdr_eth_from, withdr_eth_to, acc_time_sleep_from, acc_time_sleep_to

infura_url = "https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
web3 = Web3(Web3.HTTPProvider(infura_url))

print("Is connected:", web3.is_connected())

file_path = 'private_keys.txt'
private_keys = []
success_file_path = 'success.txt'

# Open the file and read the lines
try:
    with open(file_path, 'r') as file:
        for line in file:
            private_key = line.strip()
            if private_key:
                private_keys.append(private_key)
except FileNotFoundError:
    print(f"The file {file_path} was not found.")

contract_address = Web3.to_checksum_address("0x4944C6268DeDD0F4d9c840B6C389a7c5C7dD473a")

def deposite(key):

    dep_eth = random.uniform(deposite_eth_from, deposite_eth_to)
    account = web3.eth.account.from_key(key)
    from_address = web3.to_checksum_address(account.address)
    nonce = web3.eth.get_transaction_count(from_address)
    tx = {
        'from': from_address,
        'to': contract_address,
        'value': web3.to_wei(dep_eth, 'ether'),  # Amount of Ether you want to send
        'data': '0xf6326fb3',  # Method ID for depositETH()
        'gasPrice':  round(1.15*web3.eth.gas_price),
        'nonce': nonce,
    }

    # Sign the transaction
    estimated_gas = web3.eth.estimate_gas(tx)
    tx['gas'] = estimated_gas

    signed_tx = web3.eth.account.sign_transaction(tx, key)

    # Send the transaction

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print('Ждем подтверждения депозита', end='')

        is_approve = web3.eth.wait_for_transaction_receipt(web3.to_hex(tx_hash), timeout=120,
                                                           poll_latency=0.1).status
        if is_approve == 1:
            cprint(f'\n>>> Transaction success | https://goerli.etherscan.io/tx/{tx_hash.hex()} ', 'green')

            return True
        else:
            cprint(f'\n>>> Transaction on private key {key} failed | https://goerli.etherscan.io/tx/{tx_hash.hex()}', 'red')
            return False

    except Exception as e:
        cprint(f'\n>>> Transaction on private key {key} failed  | \n{str(e)}', 'red')
        return False


def withdrawl(key):
    withdr_eth = random.uniform(withdr_eth_from, withdr_eth_to)
    account = web3.eth.account.from_key(key)
    from_address = web3.to_checksum_address(account.address)
    nonce = web3.eth.get_transaction_count(from_address)

    withdrawal_amount = int(withdr_eth * pow(10, 18))  # For 1 token, assuming 18 decimals
    data = '0xda95ebf7' + \
           '000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee' + \
           web3.to_hex(withdrawal_amount)[2:].rjust(64, '0')

    tx = {
        'from': from_address,
        'to': contract_address,
        'data': data,
        'gasPrice':  round(1.15*web3.eth.gas_price),
        'nonce': nonce,
    }


    # Sign the transaction
    estimated_gas = web3.eth.estimate_gas(tx)
    tx['gas'] = estimated_gas

    signed_tx = web3.eth.account.sign_transaction(tx, key)

    # Send the transaction

    try:

        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print('Ждем подтверждения вывода', end='')

        is_approve = web3.eth.wait_for_transaction_receipt(web3.to_hex(tx_hash), timeout=120,
                                                           poll_latency=0.1).status
        if is_approve == 1:
            cprint(f'\n>>> Transaction success | https://goerli.etherscan.io/tx/{tx_hash.hex()} ', 'green')
            return True

        else:
            cprint(f'\n>>> Transaction on private key {key} failed | https://goerli.etherscan.io/tx/{tx_hash.hex()}', 'red')
            return False

    except Exception as e:
        cprint(f'\n>>> Transaction failed {key} | \n{str(e)}', 'red')
        return False


def append_success_key(key):
    try:
        with open(success_file_path, 'a') as file:
            file.write(key + '\n')
    except Exception as e:
        print(f"Error writing key to file: {e}")

def main():
    cprint(f'\n============================================= 0rex =============================================',
           'cyan')
    for key in private_keys:
        try:
            tx_count = random.randint(iterations_from, iterations_to)
            success_first_dep = deposite(key)
            if not success_first_dep:
                continue
            time_to_sleep = random.randint(time_sleep_from, time_sleep_to)
            cprint(f'Сплю {time_to_sleep} секунд', 'blue')
            time.sleep(time_to_sleep)
            for i in range(tx_count):
                type_tx = random.randint(1, 2)
                if type_tx == 1:
                    deposite(key)
                else:
                   withdrawl(key)
                time_to_sleep = random.randint(time_sleep_from, time_sleep_to)
                cprint(f'Сплю {time_to_sleep} секунд между транзами', 'blue')
                time.sleep(time_to_sleep)
            append_success_key(key)
        except Exception as e:
            cprint(f"Ошибка на приватнике {key}, перехожу к следующему: \n{str(e)}", 'red')
    time_to_sleep_between_accs = random.randint(acc_time_sleep_from, acc_time_sleep_to)
    cprint(f'Сплю {time_to_sleep_between_accs} секунд между акками', 'blue')
    time.sleep(time_to_sleep_between_accs)


if __name__ == '__main__':
    main()
