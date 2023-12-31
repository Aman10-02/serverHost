import time
# from time import time
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
from pprint import pprint

class Blockchain():
    def __init__(self):
        self.chain = []
        # self.__secret = ''
        self.__difficulty = 4 
        self.nodes = set()
        self.clients = {}
        # i = 0
        # secret_string = '/*SECRET*/'
        # while True:
        #     _hash = hashlib.sha256(str(secret_string+str(i)).encode('utf-8')).hexdigest()
        #     if(_hash[:self.__difficulty] == '0'*self.__difficulty):
        #         self.__secret = _hash
        #         break
        #     i+=1
        # self.__secret_block = self.create_block(sender = 'N.A' , receiver = 'N.A' , information = 'N.A')
        self.create_block(sender = 'N.A' , receiver = 'N.A' , information = 'N.A')
    def create_block(self, sender:str, receiver:str,information:str):
        block = {
            'index': len(self.chain),
            'sender': sender,
            'receiver': receiver,
            'timestamp': str(time.strftime("%d %B %Y , %I:%M:%S %p", time.localtime())),  # d-date, B-Month, Y-Year ,I-Hours in 12hr format, M-Minutes, S-secnods, p-A.M or P.M,
            'file_unique_id': information
        }
        # if(block['index'] == 0): block['previous_hash'] = self.__secret 
        if(block['index'] == 0): block['previous_hash'] = '#' 
        else: block['previous_hash'] = self.chain[-1]['hash']
        i = 0
        while True:
            block['nonce'] = i
            _hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                block['hash'] = _hash
                break
            i+=1
        self.chain.append(block)
    def validate_blockchain(self, chain):
        valid = True
        n = len(chain)-1
        i = 0
        while(i<n):
            if(chain[i]['hash'] != chain[i+1]['previous_hash']):
                valid = False
                break
            i+=1
        if valid: 
            print('The blockchain is valid...')
            return valid
        else: 
            print('The blockchain is not valid...')
            return valid

    # def show_blockchain(self):
    #     for block in self.chain: 
    #         pprint(block)
    #         print()


# class Blockchain:

#     def __init__(self):
#         self.chain = []
#         self.create_block(proof = 1, previous_hash = '0' , sender = 'N.A' , receiver = 'N.A' , file_hash = 'N.A') ##########
#         self.nodes = set()
#         # self.nodes.add(app.config['SERVER_IP'])
#         # self.nodes.add(app.config['SERVER_IP'])
    
#     def create_block(self, proof, previous_hash, sender, receiver, file_hash):
#         block = {'index': len(self.chain) + 1,
                #  'timestamp': str(time.strftime("%d %B %Y , %I:%M:%S %p", time.localtime())),  # d-date, B-Month, Y-Year ,I-Hours in 12hr format, M-Minutes, S-secnods, p-A.M or P.M
#                  'proof': proof,
#                  'previous_hash': previous_hash,
#                  'sender': sender, #########
#                  'receiver':receiver, #########
#                  'shared_files': file_hash}
#         # self.shared_files = []
#         # self.sender = [] #########
#         # self.receiver = [] ########
#         self.chain.append(block)
#         return block

#     def get_previous_block(self):
#         return self.chain[-1]

#     def proof_of_work(self, previous_proof):
#         new_proof = 1
#         check_proof = False
#         while check_proof is False:
#             hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
#             if hash_operation[:4] == '0000':
#                 check_proof = True
#             else:
#                 new_proof += 1
#         return new_proof
    
#     def hash(self, block):
#         encoded_block = json.dumps(block, sort_keys = True).encode()
#         return hashlib.sha256(encoded_block).hexdigest()
    
#     def is_chain_valid(self, chain):
#         previous_block = chain[0]
#         block_index = 1
#         while block_index < len(chain):
#             block = chain[block_index]
#             if block['previous_hash'] != self.hash(previous_block):
#                 return False
#             previous_proof = previous_block['proof']
#             proof = block['proof']
#             hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
#             if hash_operation[:4] != '0000':
#                 return False
#             previous_block = block
#             block_index += 1
#         return True
    
#     def add_file(self, sender, receiver, file_hash):
#         # self.sender.append({'sender': sender}) #########
#         # self.receiver.append({'receiver': receiver}) ##########
#         # self.shared_files.append({'file_hash': file_hash})

#         previous_block = self.get_previous_block()
#         index = previous_block['index'] + 1
#         # To be changed to 10 later
#         # if len(self.shared_files) == 1 and len(self.sender) == 1 and len(self.receiver) == 1: #########
#         previous_proof = previous_block['proof']
#         proof = self.proof_of_work(previous_proof)
#         previous_hash = self.hash(previous_block)
#         self.create_block(proof, previous_hash, sender, receiver, file_hash)
#         return index
    
#     # def replace_chain(self):
#     #     network = self.nodes
#     #     print(network)
#     #     longest_chain = None
#     #     max_length = len(self.chain)
#     #     for node in network:
#     #         # response = requests.get(f'http://{node}/get_chain')
#     #         response = requests.get(f'{node}/get_chain')
#     #         if response.status_code == 200:
#     #             length = response.json()['length']
#     #             chain = response.json()['chain']
#     #             if length > max_length and self.is_chain_valid(chain):
#     #                 max_length = length
#     #                 longest_chain = chain
#     #     if longest_chain:
#     #         self.chain = longest_chain
#     #         return True
#     #     return False
    
