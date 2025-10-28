import random
import base58
import ecdsa
import requests
from eth_hash.auto import keccak as keccak_256
from rich import print
import time

# --- КОНСТАНТЫ ---
# Token ID для USDT TRC-20 на Tron
USDT_TOKEN_ID = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def keccak256(data):
    return keccak_256(data)

def get_signing_key(raw_priv):
	return ecdsa.SigningKey.from_string(raw_priv, curve=ecdsa.SECP256k1)

def verifying_key_to_addr(key):
	pub_key = key.to_string()
	primitive_addr = b'\x41' + keccak256(pub_key)[-20:]
	addr = base58.b58encode_check(primitive_addr)
	return addr

z = 0
w = 0

print("[b red]--- TRON & USDT RANDOM KEY CHECKER STARTED ---[/]")

while True:
    try:
        # 1. Генерация ключа
        raw = bytes(random.sample(range(0, 256), 32))
        key = get_signing_key(raw)
        addr = verifying_key_to_addr(key.get_verifying_key()).decode()
        priv = raw.hex()
        
        # 2. Запрос к API
        block = requests.get("https://apilist.tronscan.org/api/account?address=" + addr)
        res = block.json()
        
        # Инициализация балансов
        trx_bal = 0.0
        usdt_bal = 0.0
        
        # --- 3. ПОИСК БАЛАНСА TRX (как было ранее) ---
        balances_list = res.get("balances", [])
        if balances_list:
            first_balance_data = balances_list[0]
            bal_str = first_balance_data.get("amount")
            if bal_str:
                trx_bal = float(bal_str)
        
        # --- 4. ПОИСК БАЛАНСА USDT ---
        trc20_balances = res.get("trc20token_balances", [])
        
        if trc20_balances:
            for token in trc20_balances:
                if token.get("tokenId") == USDT_TOKEN_ID:
                    # Баланс токенов часто хранится в поле 'balance' как целое число (с децималами)
                    # или в поле 'amount' как float.
                    # Поле 'amount' более удобное, если оно есть.
                    usdt_amount = token.get("amount")
                    if usdt_amount:
                        usdt_bal = float(usdt_amount)
                    # Если 'amount' отсутствует, нужно использовать 'balance' и 'tokenDecimal'
                    elif token.get("balance") and token.get("tokenDecimal") is not None:
                        # Конвертация: balance / 10^decimal
                        balance_raw = int(token.get("balance"))
                        decimals = int(token.get("tokenDecimal"))
                        usdt_bal = balance_raw / (10 ** decimals)
                    break # Нашли USDT, можно выходить из цикла
        
        # --- 5. Обработка результатов (если найден любой ненулевой баланс) ---
        if trx_bal > 0 or usdt_bal > 0:
            w += 1
            
            # Формирование строки балансов для файла
            balance_output = f'TRX: {trx_bal}, USDT: {usdt_bal}'

            # Запись в файл: используем f-строки для чистоты
            with open("results/FileTRXWinner.txt", "a") as f:
                f.write(f'\n[WINNER FOUND - {time.ctime()}]')
                f.write(f'\nADDReSS: {addr}   Balance: {balance_output}')
                f.write(f'\nPRIVATEKEY: {priv}')
                f.write('\n------------------------\n')
            
            # Вывод на консоль
            print(f'[green bold]>>> WINNER! <<<[/]')
            print(f'[green bold]Total Scans: {z}[/] [green bold]WINNERS: {w}[/]')
            print(f'[green bold]Address: [/]{addr}')
            print(f'[green bold]Balances: TRX={trx_bal}, USDT={usdt_bal}[/]')
            print(f'[green bold]Private Key: [/][red bold]{priv}[/]')
            print("[b green]------------------------[/]")

        else:
            # Вывод для пустого адреса
            print(f'[red1]Total Scan: [/][b blue]{z}[/]', end=' ')
            print(f'[gold1]Address: [/]{addr} [yellow]TRX Balance: {trx_bal}, USDT Balance: {usdt_bal}[/]')
            print(f'[gold1]Private Key: [/][red1]{priv}[/]')
            
        z += 1
        
    except requests.exceptions.RequestException as e:
        print(f"[bold red]NETWORK ERROR:[/bold red] {e}. Waiting 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        print(f"[bold yellow]UNEXPECTED ERROR:[/bold yellow] {e}. Skipping this address.")
        time.sleep(1)
