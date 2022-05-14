import sys
from uuid import uuid4

from flask import Flask
from flask.globals import request
from flask.json import jsonify

from blockchain import Blockchain

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


# Route
@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.add_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    last_block_hash = blockchain.hash_block(blockchain.last_block)

    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transactions)

    block = blockchain.append_block(nonce, last_block_hash)

    response = {
        'message': 'New Block has been mined',
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transaction': block['transaction']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields):
        return 'Missing fields', 400

    index = blockchain.add_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    response = {
        'message': f'Transaction will be add to block {index}'
    }

    return jsonify(response), 201


@app.route('/nodes/add', methods=['POST'])
def add_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return 'Missing nodes info', 400

    for node in nodes:
        blockchain.add_nodes(node)

    response = {
        'message': 'New node has been added',
        'nodes': list(blockchain.nodes)
    }

    return jsonify(response), 200


@app.route('/nodes/sync', methods=['GET'])
def sync_nodes():
    updated = blockchain.update_blockchain()

    if updated:
        response = {
            'message': 'Blockchain has been updated with new data',
            'blockchain': blockchain.chain
        }
    else:
        response = {
            'message': 'Blockchain is up to date',
            'blockchain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
