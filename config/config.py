import os
import sys
from pathlib import Path


# Путь к директории
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()


# ABI контрактов
ABIS_DIR = os.path.join(ROOT_DIR, 'ABI')
NFT_ABI = os.path.join(ABIS_DIR, 'nft.json')
BRIDGE_ABI = os.path.join(ABIS_DIR, 'bridge.json')
CLAIM_ABI = os.path.join(ABIS_DIR, 'claim.json')


# Приватные ключи
PRIVATE_KEYS_FILE = os.path.join(f'{ROOT_DIR}\wallet\private_key.txt')
with open(PRIVATE_KEYS_FILE) as private_key:
    private_keys = [key.strip() for key in private_key.readlines()]


# RPC ноды
bnb_rpc = 'https://bsc-dataseed1.defibit.io'
opbnb_rpc = 'https://opbnb-testnet-rpc.bnbchain.org'
