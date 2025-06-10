const socket = io();
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const fileInput = document.getElementById('file-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');

const username = prompt("Enter your name") || "Anonymous";

// Events
sendBtn.addEventListener('click', () => {
    sendMessage();
    sendFile();
});
voiceBtn.addEventListener('click', startVoice);

// Text message listener
socket.on('chat_message', function (data) {
    const div = document.createElement('div');
    div.className = 'message';
    div.innerHTML = `<strong>${data.username}</strong> [${data.timestamp}]: ${data.message}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Media message listener
socket.on('media_message', function (data) {
    const div = document.createElement('div');
    div.className = 'message';
    div.innerHTML = `<strong>${data.username}</strong> [${data.timestamp}]:<br>`;

    if (data.fileType.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = data.fileData;
        img.style.maxWidth = '200px';
        div.appendChild(img);
    } else if (data.fileType.startsWith('video/')) {
        const video = document.createElement('video');
        video.src = data.fileData;
        video.controls = true;
        video.style.maxWidth = '200px';
        div.appendChild(video);
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Functions
function sendMessage() {
    const msg = chatInput.value;
    if (msg.trim()) {
        socket.emit('send_message', {
            username: username,
            message: msg
        });
        chatInput.value = '';
    }
}

function sendFile() {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function () {
        socket.emit('send_media', {
            username: username,
            fileData: reader.result, // base64 string
            fileType: file.type
        });
        fileInput.value = '';
    };
    reader.readAsDataURL(file);
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        sendMessage();
    };

    recognition.onerror = function (event) {
        console.error('Voice recognition error:', event);
    };
}


const cameraBtn = document.getElementById('camera-btn');
const preview = document.getElementById('preview');
const snapshotCanvas = document.getElementById('snapshot');

let mediaStream = null;

cameraBtn.addEventListener('click', async () => {
    if (!mediaStream) {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            preview.srcObject = mediaStream;
            preview.style.display = 'block';

            setTimeout(() => {
                takePhoto();
            }, 3000); // auto-capture after 3 seconds
        } catch (err) {
            alert("Camera access denied or not available.");
            console.error(err);
        }
    } else {
        takePhoto();
    }
});

function takePhoto() {
    const context = snapshotCanvas.getContext('2d');
    snapshotCanvas.width = preview.videoWidth;
    snapshotCanvas.height = preview.videoHeight;
    context.drawImage(preview, 0, 0, preview.videoWidth, preview.videoHeight);

    const imageData = snapshotCanvas.toDataURL('image/png');

    socket.emit('send_media', {
        username: username,
        fileData: imageData,
        fileType: 'image/png'
    });

    stopCamera();
}

function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
        preview.style.display = 'none';
    }
}
