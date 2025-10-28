from flask import Flask, request, jsonify, send_file
import os
import socket
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)

# Store connected clients
connected_clients = {}

@app.route('/')
def home():
    return "File Manager Server is running"

@app.route('/register', methods=['POST'])
def register_client():
    data = request.json
    client_name = data.get('client_name')
    client_ip = request.remote_addr
    
    connected_clients[client_name] = {
        'ip': client_ip,
        'name': client_name,
        'last_seen': socket.gethostname()
    }
    
    print(f"Client registered: {client_name} from {client_ip}")
    return jsonify({'status': 'success'})

@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(connected_clients)

@app.route('/file_list/<client_name>', methods=['GET'])
def get_file_list(client_name):
    path = request.args.get('path', '')
    client_data = connected_clients.get(client_name)
    
    if not client_data:
        return jsonify({'error': 'Client not found'}), 404
    
    # In a real implementation, this would forward to the actual client
    # For demo, we'll return local files
    try:
        target_path = path if path else os.getcwd()
        items = os.listdir(target_path)
        
        files = []
        directories = []
        
        for item in items:
            item_path = os.path.join(target_path, item)
            if os.path.isfile(item_path):
                files.append({
                    'name': item,
                    'size': os.path.getsize(item_path),
                    'type': 'file'
                })
            else:
                directories.append({
                    'name': item,
                    'type': 'directory'
                })
        
        return jsonify({
            'path': target_path,
            'files': files,
            'directories': directories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/read_file/<client_name>', methods=['GET'])
def read_file(client_name):
    file_path = request.args.get('path')
    
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_file/<client_name>', methods=['POST'])
def delete_file(client_name):
    data = request.json
    path = data.get('path')
    
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    try:
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_file/<client_name>', methods=['POST'])
def create_file(client_name):
    data = request.json
    path = data.get('path')
    content = data.get('content', '')
    
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_directory/<client_name>', methods=['POST'])
def create_directory(client_name):
    data = request.json
    path = data.get('path')
    
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    try:
        os.makedirs(path, exist_ok=True)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=10000, debug=True)
