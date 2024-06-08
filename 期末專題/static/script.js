const socket = io();

function updateFileList(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    files.forEach(file => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = `/download/${file}`;
        link.textContent = file;
        const icon = document.createElement('i');
        icon.className = 'fas fa-download';
        link.prepend(icon);
        li.appendChild(link);
        fileList.appendChild(li);
    });
}

socket.on('file_list', (files) => {
    updateFileList(files);
});

socket.emit('file_list');
