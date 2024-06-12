from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TRASH_FOLDER'] = 'trash'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TRASH_FOLDER'], exist_ok=True)
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

    files = []
    dirs = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            dirs.append(entry)
        else:
            files.append(entry)
    return render_template('index.html', subpath=subpath, files=files, dirs=dirs)


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
    if subpath == 'trash':
        folder_path = app.config['TRASH_FOLDER']
    else:
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


@socketio.on('open_file')
def handle_open_file(data):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], data['subpath'], data['filename'])
    if data['filename'].endswith('.txt'):
        with open(filepath, 'r') as file:
            content = file.read()
        emit('file_content', {'filename': data['filename'], 'content': content})
    else:
        emit('file_content', {'filename': data['filename'], 'content': None})


@socketio.on('save_file')
def handle_save_file(data):
    filename = data['filename']
    if not filename.endswith('.txt'):
        filename += '.txt'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], data['subpath'], filename)
    with open(filepath, 'w') as file:
        file.write(data['content'])
    emit('file_saved', {'filename': filename, 'content': data['content']})


@socketio.on('edit_file')
def handle_edit_file(data):
    emit('file_content', data, broadcast=True)


@socketio.on('delete_file')
def handle_delete_file(data):
    filename = data['filename']
    subpath = data['subpath']
    src_path = os.path.join(app.config['UPLOAD_FOLDER'], subpath, filename)
    dest_path = os.path.join(app.config['TRASH_FOLDER'], filename)
    shutil.move(src_path, dest_path)
    emit('file_deleted', {'filename': filename})


@socketio.on('restore_file')
def handle_restore_file(data):
    filename = data['filename']
    src_path = os.path.join(app.config['TRASH_FOLDER'], filename)
    dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    shutil.move(src_path, dest_path)
    emit('file_restored', {'filename': filename})


@socketio.on('empty_trash')
def handle_empty_trash():
    for filename in os.listdir(app.config['TRASH_FOLDER']):
        file_path = os.path.join(app.config['TRASH_FOLDER'], filename)
        os.remove(file_path)
    emit('trash_emptied')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
