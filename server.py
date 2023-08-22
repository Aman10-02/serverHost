import os
import time
import urllib.request
import ipfshttpclient
from my_constants import app, socketio
import pyAesCrypt
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
from public_private import generate_and_store_keys
from key_management import get_str_from_key
from upload_function import encrypt_upload
from download_function import main_decrypt
# from web3storage import Client
# import socket
import pickle
from blockchain import Blockchain
import requests

# import os

HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5111))
# The package requests is used in the 'hash_user_file' and 'retrieve_from hash' functions to send http post requests.
# Notice that 'requests' is different than the package 'request'.
# 'request' package is used in the 'add_file' function for multiple actions.

# socketio = SocketIO(app)
blockchain = Blockchain()
my_key= ''
my_name = ''
async def replace_chain():
    network = blockchain.nodes
    longest_chain = None
    max_length = len(blockchain.chain)

    def res(data) :
        print("data", data)
        nonlocal longest_chain, max_length
        length = data['length']
        chain = data['chain']
        if length > max_length and blockchain.validate_blockchain(chain):
            print("inside")
            max_length = length
            blockchain.chain = chain
    
    for node in network:
        socketio.emit('get_chain', {}, room = node, callback = res)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html' , message = "Welcome!")

@app.route('/download')
def download():
    return render_template('download.html' , message = "Welcome!")

@app.route('/connect_blockchain')
async def connect_blockchain():
    print("con")
    global connection_status
    global my_key, my_name
    nodes = len(blockchain.nodes)

    if os.path.exists("./private_key.pem"):
        print("File exists!")
        with open('public.txt', 'r') as fl:
            my_key = fl.read()
        with open('username.txt', 'r') as nm:
            my_name = nm.read()
    else:
        generate_and_store_keys()
        my_key = get_str_from_key()
        my_name = str(int(time.time()))
        with open('username.txt', 'w') as userfile:
            userfile.write(my_name)

    blockchain.clients[my_name] = my_key
    await replace_chain()
    return render_template('connect_blockchain.html', chain = blockchain.chain, nodes = len(blockchain.nodes), userName = my_name)

@app.errorhandler(413)
def entity_too_large(e):
    return render_template('upload.html' , message = "Requested Entity Too Large!")

@app.route('/add_file', methods=['POST'])
async def add_file():

    if request.method == 'POST':
        error_flag = True
        if 'file' not in request.files:
            message = 'No file part'
        else:
            user_file = request.files['file']
            receiver = request.form['receiver_name']
            receiver_key = ''
            if user_file.filename == '':
                message = 'No file selected for uploading'

            if receiver not in blockchain.clients:
                message = 'Invalid Receiver'
            else:
                receiver_key = blockchain.clients[receiver]

            if receiver_key and user_file and allowed_file(user_file.filename):
                error_flag = False
                filename = secure_filename(user_file.filename)
                file_path = os.path.join("./uploads", filename)
                print(file_path)
                user_file.save(file_path)
                    
                try:
                    def cb(data) :
                        if data.get("flag") == False :
                            nonlocal error_flag, message
                            error_flag = True
                            message = 'Could not complete. Try again !!'
                    # hashed_output1 = hash_user_file(file_path, file_key)
                    hashed_output1 = encrypt_upload(file_path, receiver_key)
                    index = blockchain.create_block(my_name, receiver, hashed_output1)
                    socketio.emit("set_chain", {"chain": blockchain.chain}, callback = cb )
                except Exception as err:
                    message = str(err)
                    error_flag = True
                    if "ConnectionError:" in message:
                        message = "Gateway down or bad Internet!"
            else:
                error_flag = True
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'
    
        if error_flag == True:
            return render_template('upload.html' , message = message)
        else:
            return render_template('upload.html' , message = "File succesfully uploaded")

@app.route('/retrieve_file', methods=['POST'])
async def retrieve_file():

    if request.method == 'POST':

        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No file hash entered.'
        else:
            error_flag = False
            file_hash = request.form['file_hash']
            try:
                main_decrypt(file_hash)
            except Exception as err:
                message = str(err)
                error_flag = True
                if "ConnectionError:" in message:
                    message = "Gateway down or bad Internet!"

        if error_flag == True:
            return render_template('download.html' , message = message)
        else:
            return render_template('download.html' , message = "File successfully downloaded")

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200  

def remove_node(client_node):
    blockchain.nodes.remove(client_node)
    socketio.emit('my_response', {'data': pickle.dumps(blockchain.nodes)})


@socketio.on('connect')
def connect():
    print(f"A user connected: {request.sid}")
    print("requests", request.sid)
    socketio.emit('me', {"id":request.sid}, room = request.sid)

@socketio.on('add_client')
def add_client(data):
    key = data.get("key")
    userName = data.get("userName")
    blockchain.clients[userName] = key
    blockchain.nodes.add(request.sid)
    socketio.emit('my_response', {'nodes': pickle.dumps(blockchain.nodes), "clients" : blockchain.clients})

@socketio.on('disconnect')
def disconnect():
    print(f"A user disconnected: {request.sid}")
    remove_node(request.sid)

@socketio.on('set_chain')
def set_chain(data):
    chain = blockchain.chain
    newchain = data.get("chain")
    if len(chain) < len(newchain) and blockchain.validate_blockchain(newchain):
        blockchain.chain = newchain
        socketio.emit('update_chain', {"chain" : blockchain.chain})
        return {"flag" : True }
    return {"flag" : False }


if __name__ == '__main__':
    # socketio.run(app, "https://eed5-14-139-196-13.ngrok-free.app", debug=True)
    # socketio.run(app, host = '127.0.0.1', port= 5111, debug=True)
    socketio.run(app, host = HOST, port= PORT, debug=True)