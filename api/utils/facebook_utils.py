import base64
import json
import requests
import os
from datetime import datetime

def encode_message(message_data):
    """Encode un message en base64 pour Facebook"""
    if isinstance(message_data, dict):
        message_data = json.dumps(message_data)
    message_bytes = message_data.encode('utf-8')
    return base64.b64encode(message_bytes).decode('utf-8')

def decode_message(encoded_message):
    """Décode un message base64 de Facebook"""
    try:
        decoded_bytes = base64.b64decode(encoded_message)
        return json.loads(decoded_bytes.decode('utf-8'))
    except:
        return None

def update_facebook_post(post_id, message):
    """Met à jour un post Facebook avec un message encodé"""
    access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    api_version = os.getenv('FACEBOOK_API_VERSION')
    
    if not access_token:
        raise ValueError("PAGE_ACCESS_TOKEN not configured")
        
    url = f'https://graph.facebook.com/{api_version}/{post_id}'
    encoded_message = encode_message(message)
    
    response = requests.post(url, data={
        'message': encoded_message,
        'access_token': access_token
    })
    
    return response.json() 