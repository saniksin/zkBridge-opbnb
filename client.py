from web3 import Web3
from web3.middleware import geth_poa_middleware

from utils import read_json
from config.config import NFT_ABI, BRIDGE_ABI


class Client:
    nft_abi = read_json(NFT_ABI)
    bridge_abi = read_json(BRIDGE_ABI)
    claim_abi = None

    def __init__(self, private_key, bnb_rpc, opbnb_prc):
        self.private_key = private_key
        self.bnb_rpc = bnb_rpc
        self.opbnb_rpc = opbnb_prc
        self.w3_bnb = Web3(Web3.HTTPProvider(endpoint_uri=self.bnb_rpc))
        self.w3_opbnb = Web3(Web3.HTTPProvider(endpoint_uri=self.opbnb_rpc))
        self.address = Web3.to_checksum_address(
            self.w3_bnb.eth.account.from_key(private_key=private_key).address
        )
        self.onion = self.w3_bnb.middleware_onion.inject(geth_poa_middleware, layer=0)

    def get_balance(self, web3):
        balance = Web3.from_wei(
            web3.eth.get_balance(self.address), 'ether')
        return balance
    
    def get_bnb_balance(self):
        balance = self.get_balance(self.w3_bnb)
        return balance
    
    def get_opbnb_balance(self):
        balance = self.get_balance(self.w3_opbnb)
        return balance