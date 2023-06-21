from web3 import Web3
from config.config import NFT_ABI, BRIDGE_ABI, CLAIM_ABI
from utils import read_json
from client import Client
from hexbytes import HexBytes
from easydict import EasyDict as AttributeDict

class ZkBridge:
    mintnft_contract = Web3.to_checksum_address('0x9885C17Dd44c00C37B98F510cdff099EfF437dcE')
    bridge_contract = Web3.to_checksum_address('0xE09828f0DA805523878Be66EA2a70240d312001e')
    claimnft_contract = Web3.to_checksum_address('0x4cc870c8fdfbc512943fe60c29c98d515f868ebf')

    mintnft_abi = read_json(NFT_ABI)
    bridge_abi = read_json(BRIDGE_ABI)
    nftclaim = read_json(CLAIM_ABI)

    def __init__(self, client: Client):
        self.client = client
        self.w3_bnb = self.client.w3_bnb
        self.w3_opbnb = self.client.w3_opbnb
        self.transaction_receipt = None
        self.token_id = None

    def check_transaction_cost(self, transaction_method, *args, value=None):
        gas_price = self.w3_bnb.eth.gas_price
        check_param = {
            'from': self.client.address,
        }
        if value is not None:
            check_param['value'] = value
        gas_estimate = transaction_method(*args).estimate_gas(check_param)
        total_cost = self.w3_bnb.from_wei(
            gas_price * gas_estimate, 'ether')
        return gas_price, gas_estimate, total_cost

    def _send_transaction(self, transaction_method, *args, value=None):
        gas_price, gas_estimate, total_cost = self.check_transaction_cost(transaction_method, *args, value=value)
        if self.client.get_bnb_balance() < total_cost:
            print(f'{self.client.address} | Не хватит bnb для выполнения транзакции')
            return None
        transaction_param = {
            'from': self.client.address,
            'nonce': self.w3_bnb.eth.get_transaction_count(self.client.address),
            'gas': int(gas_estimate * 1.2),
            'gasPrice': gas_price,
        }
        if value is not None:
            transaction_param['value'] = value
        transaction = transaction_method(*args).build_transaction(transaction_param)

        signed_txn = self.w3_bnb.eth.account.sign_transaction(transaction, private_key=self.client.private_key)
        transaction_hash = self.w3_bnb.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.w3_bnb.eth.wait_for_transaction_receipt(transaction_hash)

    def mint_nft(self):
        contract = self.w3_bnb.eth.contract(
            abi=ZkBridge.mintnft_abi,
            address=ZkBridge.mintnft_contract
        )
        self.transaction_receipt = self._send_transaction(contract.functions.mint)
        
        if self.transaction_receipt and self.transaction_receipt.status == 1:
            print(f'{self.client.address} | Успешно сминтил нфт')
        else:
            print(f'{self.client.address} | Не удалось сминить нфт')

    def approve_nft(self):
        contract = self.w3_bnb.eth.contract(
            abi=ZkBridge.mintnft_abi,
            address=ZkBridge.mintnft_contract
        )
        token_id_hex = self.transaction_receipt['logs'][0]['topics'][3].hex()
        self.token_id = int(token_id_hex, 16)
        self.transaction_receipt = self._send_transaction(
                                        contract.functions.approve, 
                                        self.bridge_contract, 
                                        self.token_id)
        
        if self.transaction_receipt and self.transaction_receipt.status == 1:
            print(f'{self.client.address} | Успешно выполнил апрув')
        else:
            print(f'{self.client.address} | Не удалось выполнить апрув')
            
    def bridge_nft(self):
        recipient_chain = 116 
        client_address_bytes32 = "0x" + self.client.address[2:].zfill(64)
        
        contract = self.w3_bnb.eth.contract(
            abi=ZkBridge.bridge_abi,
            address=ZkBridge.bridge_contract
        )

        value = Web3.to_wei(0.001, 'ether')

        self.transaction_receipt = self._send_transaction(
                                    contract.functions.transferNFT,
                                    self.mintnft_contract,
                                    self.token_id,
                                    recipient_chain,
                                    client_address_bytes32,
                                    value=value,
                                    )
        
        print(self.transaction_receipt)
        if self.transaction_receipt and self.transaction_receipt.status == 1:
            print(f'{self.client.address} | Успешно отправил нфт через мост')
        else:
            print(f'{self.client.address} | Не удалось отправить нфт')

    def claim_nft(self):
        pass
        # contract = self.w3_opbnb.eth.contract(
        #     address=ZkBridge.claimnft_contract,
        #     abi=self.nftclaim,
        # )

        # transaction_receipt = AttributeDict({'blockHash': HexBytes('0xff99b634c11541f35f7775c5dcc413d50f743cb92036c7bf71874d423ab93e65'), 'blockNumber': 29284947, 'contractAddress': None, 'cumulativeGasUsed': 13798309, 'effectiveGasPrice': 3000000000, 'from': '0x27DA5E1f74d16DBc2E0A113b134EdAB5e2BcbB7d', 'gasUsed': 103435, 'logs': [AttributeDict({'address': '0x9885C17Dd44c00C37B98F510cdff099EfF437dcE', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000027da5e1f74d16dbc2e0a113b134edab5e2bcbb7d'), HexBytes('0x000000000000000000000000e09828f0da805523878be66ea2a70240d312001e'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000031066')], 'data': HexBytes('0x'), 'blockNumber': 29284947, 'transactionHash': HexBytes('0xa6a0ef47cfa2d41e13420a59dbf8f62386a891cac6f0e7b2ac2ae80d609bd58d'), 'transactionIndex': 80, 'blockHash': HexBytes('0xff99b634c11541f35f7775c5dcc413d50f743cb92036c7bf71874d423ab93e65'), 'logIndex': 284, 'removed': False}), AttributeDict({'address': '0xe9AD444cF80E1d6Ba062A2Dd6f53b740b5F0aa14', 'topics': [HexBytes('0xb8abfd5c33667c7440a4fc1153ae39a24833dbe44f7eb19cbe5cd5f2583e4940'), HexBytes('0x000000000000000000000000e09828f0da805523878be66ea2a70240d312001e'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000000074'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000108a49')], 'data': HexBytes('0x000000000000000000000000ba09fdf988d4113460dbdd96fefd33c8400e4e0d000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000f6010000000000000000000000009885c17dd44c00c37b98f510cdff099eff437dce0003424e4220436861696e204c7562616e2055706772616465000000000000000000424e4220436861696e204c7562616e205570677261646500000000000000000000000000000000000000000000000000000000000000000000000000000310665068747470733a2f2f676174657761792e70696e6174612e636c6f75642f697066732f516d526e73764647334d524351785438534e346366544765504357724d535656436a357879335774325476316e7600000000000000000000000027da5e1f74d16dbc2e0a113b134edab5e2bcbb7d007400000000000000000000'), 'blockNumber': 29284947, 'transactionHash': HexBytes('0xa6a0ef47cfa2d41e13420a59dbf8f62386a891cac6f0e7b2ac2ae80d609bd58d'), 'transactionIndex': 80, 'blockHash': HexBytes('0xff99b634c11541f35f7775c5dcc413d50f743cb92036c7bf71874d423ab93e65'), 'logIndex': 285, 'removed': False}), AttributeDict({'address': '0xE09828f0DA805523878Be66EA2a70240d312001e', 'topics': [HexBytes('0xe11d2ca26838f15acb41450029a785bb3d6f909b7f622ebf9c45524ded76f411'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000108a49')], 'data': HexBytes('0x0000000000000000000000009885c17dd44c00c37b98f510cdff099eff437dce0000000000000000000000000000000000000000000000000000000000031066000000000000000000000000000000000000000000000000000000000000007400000000000000000000000027da5e1f74d16dbc2e0a113b134edab5e2bcbb7d00000000000000000000000027da5e1f74d16dbc2e0a113b134edab5e2bcbb7d'), 'blockNumber': 29284947, 'transactionHash': HexBytes('0xa6a0ef47cfa2d41e13420a59dbf8f62386a891cac6f0e7b2ac2ae80d609bd58d'), 'transactionIndex': 80, 'blockHash': HexBytes('0xff99b634c11541f35f7775c5dcc413d50f743cb92036c7bf71874d423ab93e65'), 'logIndex': 286, 'removed': False})], 'logsBloom': HexBytes('0x00000000000000400000000002000400000000400000000000000000000000000000000000000000000000000000000008000800010000000000200000000000000000000100000000010008080002000000000000000000001000000000000080000000000000000000000000000100000000000000000000000010000000000000000000000000000000001400080000000000000040000000100000000000000000000080000000000000000000000000000804000000000000000080000000000002100008000000000100000000000000000000000000000000000000040000000020000000000000000000000000000000000000000000000000000000'), 'status': 1, 'to': '0xE09828f0DA805523878Be66EA2a70240d312001e', 'transactionHash': HexBytes('0xa6a0ef47cfa2d41e13420a59dbf8f62386a891cac6f0e7b2ac2ae80d609bd58d'), 'transactionIndex': 80, 'type': 0})

        # srcChainId = 56
        # transaction_hash = transaction_receipt['transactionHash'].hex()
        # transaction_index = transaction_receipt['transactionIndex']