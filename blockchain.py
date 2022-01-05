import sys
import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask
from flask.globals import request
from flask.json import jsonify

import requests
from urllib.parse import urlparse


class Blockchain(object):
    diffictuly_target = "0000"

    def has_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()

    def __init__(self):
        self.chain = []

        self.current_transactions = []

        genesis_hash = self.has_block("genesis_block")

        self.append_block(
            hash_of_previous_block=genesis_hash,
            nonce=self.proof_of_work(0, genesis_hash, [])
        )

    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        return nonce

    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.diffictuly_target)] == self.diffictuly_target

    def append_block(self, hash_of_previous_block, nonce):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transaction': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }

        self.current_transactions = []

        self.chain.append(block)
        return block

    def add_transaction(self, sender, repicient, amount):
        self.current_transactions.append({
            'amount': amount,
            'sender': sender,
            'repicient': repicient,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', "")

blockchain = Blockchain()

# routes


@ app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.add_transaction(
        sender=0,
        repicient=node_identifier,
        amount=1
    )

    last_block_hash = blockchain.hash_block(blockchain.last_block)
    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(
        index, last_block_hash, blockchain.current_transactions)

    block = blockchain.append_block(nonce, last_block_hash)
    response = {
        'messege': "block baru telah di {mined}",
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transaction': block['transaction'],
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_trasaction():
    values = requests.get_json()

    required_files = ['sender', 'repicient', 'amount']
    if not all(k in values for k in required_fields):
        return "missing fields"

    index = blockchain.add_trasactions[
        values['sender'],
        values['repicient'],
        values['amount']
    ]

    response = {'messege': f'transaksi akan ditambahkan ke blok {index}'}
    return (jsonify(response), 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
