import random
import base58
import ecdsa
import requests
from eth_hash.auto import keccak as keccak_256
from rich import print
import time # Добавлено для возможного использования
# Импорты base64, sys, os, subprocess не используются, но оставлены, если понадобятся.

def keccak256(data):
    # Использует keccak из eth-hash (по умолчанию keccak-256)
    return keccak_256(data)

def get_signing_key(raw_priv):
	return ecdsa.SigningKey.from_string(raw_priv, curve=ecdsa.SECP256k1)

def verifying_key_to_addr(key):
	pub_key = key.to_string()
	# Префикс '41' для Tron
	primitive_addr = b'\x41' + keccak256(pub_key)[-20:]
	addr = base58.b58encode_check(primitive_addr)
	return addr

# Эта функция valtxid была лишней и удалена.

z = 0
w = 0

print("[b red]--- TRON RANDOM KEY CHECKER STARTED ---[/]")

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
        
        # 3. БЕЗОПАСНАЯ ПРОВЕРКА БАЛАНСА
        # Используем .get() для безопасного доступа к ключу 'balances'
        # Если 'balances' отсутствует, вернется пустой список [].
        balances_list = res.get("balances", [])
        
        bal = 0.0
        
        # Проверяем, что список балансов не пуст
        if balances_list:
            # TronScan возвращает список токенов; мы ищем баланс TRX 
            # (который часто является первым элементом или единственным элементом, если нет токенов)
            # В вашем оригинальном коде была попытка взять [0], что подходит для TRX
            first_balance_data = balances_list[0]
            
            # Получаем значение 'amount'. Если его нет, используем 0.
            bal_str = first_balance_data.get("amount")
            if bal_str:
                bal = float(bal_str)
            
        # 4. Обработка результатов
        if bal > 0:
            w += 1
            # Запись в файл: используем f-строки для чистоты
            with open("results/FileTRXWinner.txt", "a") as f:
                f.write(f'\n[WINNER FOUND - {time.ctime()}]')
                f.write(f'\nADDReSS: {addr}   Balance: {bal}')
                f.write(f'\nPRIVATEKEY: {priv}')
                f.write('\n------------------------\n')
            
            # Вывод на консоль
            print(f'[green bold]>>> WINNER! <<<[/]')
            print(f'[green bold]Total Scans: {z}[/] [green bold]WINNERS: {w}[/]')
            print(f'[green bold]Address: [/]{addr} [green bold]Balance: {bal}[/]')
            print(f'[green bold]Private Key: [/][red bold]{priv}[/]')
            print("[b green]------------------------[/]")

        else:
            # Вывод для пустого адреса
            print(f'[red1]Total Scan: [/][b blue]{z}[/]', end=' ')
            print(f'[gold1]Address: [/]{addr} [yellow]Balance: {bal}[/]')
            print(f'[gold1]Private Key: [/][red1]{priv}[/]')
            
        z += 1
        
    except requests.exceptions.RequestException as e:
        # Обработка ошибок сети (таймауты, отключение)
        print(f"[bold red]NETWORK ERROR:[/bold red] {e}. Waiting 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        # Обработка других неожиданных ошибок (например, неверный формат JSON)
        # В идеале нужно узнать, почему API вернул неожиданный ответ
        print(f"[bold yellow]UNEXPECTED ERROR:[/bold yellow] {e}. Skipping this address.")
        time.sleep(1) # Небольшая пауза перед следующей попыткой
        
# Конец скрипта

