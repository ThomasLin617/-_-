from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app)

def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    create_folder_if_not_exists(folder_path)
    if os.path.isfile(folder_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], subpath)
    return render_template('index.html', subpath=subpath)

@app.route('/upload', methods=['POST'])
def upload_file():
    folder = request.form.get('folder', '')
    create_folder_if_not_exists(os.path.join(app.config['UPLOAD_FOLDER'], folder))
    if 'file' not in request.files:
        return redirect(url_for('index', subpath=folder))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index', subpath=folder))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], folder, file.filename)
        file.save(filepath)
        return redirect(url_for('index', subpath=folder))

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('file_list')
def handle_file_list(data):
    subpath = data.get('subpath', '')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath)
    files = []
    dirs = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)
    emit('file_list', {'files': files, 'dirs': dirs, 'subpath': subpath})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
