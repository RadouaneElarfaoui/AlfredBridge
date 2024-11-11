from flask import Flask, request, Response
import hmac
import hashlib
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN', 'your_verify_token')
    print(VERIFY_TOKEN)
    
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge
        else:
            return Response('Forbidden', status=403)
    
    return Response('Bad Request', status=400)

@app.route('/webhook', methods=['POST'])
def webhook_handle():
    app_secret = os.environ.get('FB_APP_SECRET')
    
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return Response('Forbidden', status=403)
    
    payload = request.get_data()
    expected_signature = 'sha256=' + hmac.new(
        app_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return Response('Forbidden', status=403)
    
    data = request.json
    
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            if 'changes' in entry:
                for change in entry['changes']:
                    if change.get('value', {}).get('item') == 'post':
                        handle_post_change(change['value'])
    
    return 'OK'

def handle_post_change(value):
    post_id = value.get('post_id')
    verb = value.get('verb')  # add, edit, delete
    
    print(f"Post {post_id} was {verb}ed")