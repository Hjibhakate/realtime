# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# from pymongo import MongoClient
# import datetime

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# # MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['voice_chat_db']
# messages_collection = db['messages']

# @app.route('/')
# def index():
#     return render_template('index.html')

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     # Load all previous messages from MongoDB
#     previous_messages = list(messages_collection.find().sort('timestamp', 1))
#     for msg in previous_messages:
#         base_data = {
#             'username': msg['username'],
#             'timestamp': msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
#         }
#         if msg.get('type') == 'media':
#             base_data.update({
#                 'fileData': msg['fileData'],
#                 'fileType': msg['fileType']
#             })
#             emit('media_message', base_data)
#         else:
#             base_data['message'] = msg['message']
#             emit('chat_message', base_data)

# @socketio.on('send_message')
# def handle_message(data):
#     username = data.get('username', 'Anonymous')
#     message = data['message']
#     timestamp = datetime.datetime.utcnow()

#     messages_collection.insert_one({
#         'type': 'text',
#         'username': username,
#         'message': message,
#         'timestamp': timestamp
#     })

#     emit('chat_message', {
#         'username': username,
#         'message': message,
#         'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")
#     }, broadcast=True)

# @socketio.on('send_media')
# def handle_media(data):
#     username = data.get('username', 'Anonymous')
#     file_data = data['fileData']
#     file_type = data['fileType']
#     timestamp = datetime.datetime.utcnow()

#     messages_collection.insert_one({
#         'type': 'media',
#         'username': username,
#         'fileData': file_data,
#         'fileType': file_type,
#         'timestamp': timestamp
#     })

#     emit('media_message', {
#         'username': username,
#         'fileData': file_data,
#         'fileType': file_type,
#         'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")
#     }, broadcast=True)

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

# if __name__ == '__main__':
#     socketio.run(app, debug=True)



from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['voice_chat_db']
messages_collection = db['messages']

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Load all previous messages from MongoDB
    previous_messages = messages_collection.find().sort('timestamp', 1)
    for msg in previous_messages:
        base_data = {
            'username': msg.get('username', 'Anonymous'),
            'timestamp': msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        }
        if msg.get('type') == 'media':
            base_data.update({
                'fileData': msg['fileData'],
                'fileType': msg['fileType']
            })
            emit('media_message', base_data)
        elif msg.get('type') == 'text':
            base_data['message'] = msg['message']
            emit('chat_message', base_data)


@socketio.on('send_message')
def handle_message(data):
    username = data.get('username', 'Anonymous')
    message = data.get('message')
    timestamp = datetime.datetime.utcnow()

    if not message:
        return  # prevent saving empty messages

    messages_collection.insert_one({
        'type': 'text',
        'username': username,
        'message': message,
        'timestamp': timestamp
    })

    emit('chat_message', {
        'username': username,
        'message': message,
        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }, broadcast=True)


@socketio.on('send_media')
def handle_media(data):
    username = data.get('username', 'Anonymous')
    file_data = data.get('fileData')
    file_type = data.get('fileType')
    timestamp = datetime.datetime.utcnow()

    if not file_data or not file_type:
        return  # prevent saving invalid media

    messages_collection.insert_one({
        'type': 'media',
        'username': username,
        'fileData': file_data,
        'fileType': file_type,
        'timestamp': timestamp
    })

    emit('media_message', {
        'username': username,
        'fileData': file_data,
        'fileType': file_type,
        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)


