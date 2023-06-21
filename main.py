from web3 import Web3
from client import Client
from config.config import private_keys, bnb_rpc, opbnb_rpc
from tasks.zkbridge import ZkBridge


clients = []
for num, key in enumerate(private_keys):
    clients.append(
        Client(private_key=key, bnb_rpc=bnb_rpc, opbnb_prc=opbnb_rpc))
    task = ZkBridge(clients[num])
    task.mint_nft()
    task.approve_nft()
    task.bridge_nft()
    #task.claim_nft()