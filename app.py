import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pymongo import MongoClient, errors
import datetime
import os
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SocketIO with eventlet async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# MongoDB setup with error handling
mongo_uri = os.environ.get("MONGODB_URI")
if not mongo_uri:
    print("ERROR: MONGODB_URI environment variable not set")
    sys.exit(1)

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Attempt a connection to check if MongoDB is reachable
    client.server_info()
except errors.ServerSelectionTimeoutError as err:
    print(f"ERROR: Could not connect to MongoDB: {err}")
    sys.exit(1)

db = client['voice_chat_db']
messages_collection = db['messages']


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect(auth):
    print('Client connected')
    try:
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
    except Exception as e:
        print(f"Error loading previous messages: {e}")


@socketio.on('send_message')
def handle_message(data):
    username = data.get('username', 'Anonymous')
    message = data.get('message')
    timestamp = datetime.datetime.utcnow()

    if not message:
        return  # prevent saving empty messages

    try:
        messages_collection.insert_one({
            'type': 'text',
            'username': username,
            'message': message,
            'timestamp': timestamp
        })
    except Exception as e:
        print(f"Insert message error: {e}")

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

    try:
        messages_collection.insert_one({
            'type': 'media',
            'username': username,
            'fileData': file_data,
            'fileType': file_type,
            'timestamp': timestamp
        })
    except Exception as e:
        print(f"Insert media error: {e}")

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




# import eventlet
# eventlet.monkey_patch()

# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit
# from pymongo import MongoClient, errors
# import datetime
# import os

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'

# # Initialize SocketIO with eventlet async mode
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# # MongoDB setup with error handling
# mongo_uri = os.environ.get("MONGODB_URI")
# if not mongo_uri:
#     raise ValueError("MONGODB_URI environment variable not set")

# try:
#     client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
#     # Attempt a connection to check if MongoDB is reachable
#     client.server_info()
# except errors.ServerSelectionTimeoutError as err:
#     print(f"ERROR: Could not connect to MongoDB: {err}")
#     # Optionally exit or continue depending on your needs
#     # exit(1)

# db = client['voice_chat_db']
# messages_collection = db['messages']


# @app.route('/')
# def index():
#     return render_template('index.html')


# @socketio.on('connect')
# def handle_connect(auth):
#     print('Client connected')
#     try:
#         previous_messages = messages_collection.find().sort('timestamp', 1)
#         for msg in previous_messages:
#             base_data = {
#                 'username': msg.get('username', 'Anonymous'),
#                 'timestamp': msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
#             }
#             if msg.get('type') == 'media':
#                 base_data.update({
#                     'fileData': msg['fileData'],
#                     'fileType': msg['fileType']
#                 })
#                 emit('media_message', base_data)
#             elif msg.get('type') == 'text':
#                 base_data['message'] = msg['message']
#                 emit('chat_message', base_data)
#     except Exception as e:
#         print(f"Error loading previous messages: {e}")


# @socketio.on('send_message')
# def handle_message(data):
#     username = data.get('username', 'Anonymous')
#     message = data.get('message')
#     timestamp = datetime.datetime.utcnow()

#     if not message:
#         return  # prevent saving empty messages

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
#     file_data = data.get('fileData')
#     file_type = data.get('fileType')
#     timestamp = datetime.datetime.utcnow()

#     if not file_data or not file_type:
#         return  # prevent saving invalid media

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
#     socketio.run(app, host='0.0.0.0', port=5000)

