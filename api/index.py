from flask import Flask, request, Response, render_template, redirect, url_for
import hmac
import hashlib
import os
import requests
import json
import datetime
from collections import deque
from typing import Dict, Deque
import time
import uuid
import base64
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Structure pour stocker l'historique
webhook_history: Deque[Dict] = deque(maxlen=int(os.getenv('MAX_HISTORY_SIZE', '100')))

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    VERIFY_TOKEN = os.getenv('FACEBOOK_VERIFY_TOKEN')
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
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    
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
    
    # Ajouter l'entrée dans l'historique
    history_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'data': data,
        'signature': signature,
        'success': True
    }
    
    try:
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change.get('value', {}).get('item') in ['post', 'status']:
                            handle_post_change(change['value'])
        webhook_history.append(history_entry)
    except Exception as e:
        history_entry['success'] = False
        history_entry['error'] = str(e)
        webhook_history.append(history_entry)
        raise
    
    return 'OK'

def handle_post_change(value):
    post_id = value.get('post_id') or value.get('status_id')
    verb = value.get('verb')
    encoded_message = value.get('message', '')
    
    try:
        # Décoder le message base64
        decoded_bytes = base64.b64decode(encoded_message)
        message = decoded_bytes.decode('utf-8')
        message_data = json.loads(message)
        
        # Valider la structure du message
        is_valid, error_message = validate_message_structure(message_data)
        
        if not is_valid:
            error_response = {
                "error": {
                    "type": "ValidationError",
                    "message": error_message,
                    "timestamp": datetime.datetime.now().isoformat()
                },
                "metadata": {
                    "type": "error",
                    "request_id": message_data.get('metadata', {}).get('request_id', str(uuid.uuid4())),
                    "platform": message_data.get('metadata', {}).get('platform', 'unknown'),
                    "api_version": message_data.get('metadata', {}).get('api_version', 'unknown')
                }
            }
            update_post(post_id, error_response)
            return
            
        # Si c'est une commande valide, traiter la requête
        if message_data.get('metadata', {}).get('type') == 'command':
            response_data = make_request(message_data)
            formatted_response = json.dumps(response_data, indent=2)
            update_post(post_id, formatted_response)
            
    except (base64.binascii.Error, json.JSONDecodeError, Exception) as e:
        error_response = {
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            },
            "metadata": {
                "type": "error",
                "request_id": str(uuid.uuid4()),
                "platform": "unknown",
                "api_version": "unknown"
            }
        }
        update_post(post_id, error_response)

def update_post(post_id, message):
    """Mettre à jour le post Facebook avec la réponse encodée en base64"""
    try:
        import base64
        access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("PAGE_ACCESS_TOKEN not configured")
            
        url = f'https://graph.facebook.com/{os.getenv("FACEBOOK_API_VERSION")}/{post_id}'
        
        # Encoder la réponse en base64
        if isinstance(message, dict):
            message = json.dumps(message)
        message_bytes = message.encode('utf-8')
        encoded_message = base64.b64encode(message_bytes).decode('utf-8')
        
        data = {
            'message': encoded_message,
            'access_token': access_token
        }
        
        print(f"Sending encoded update request to {url}")
        print(f"Original message: {message}")
        print(f"Encoded message: {encoded_message}")
        
        response = requests.post(url, data=data)
        response_data = response.json()
        print(f"Update response: {json.dumps(response_data, indent=2)}")
        
        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Request error updating post {post_id}: {str(e)}")
        if hasattr(e.response, 'json'):
            print(f"Error response: {json.dumps(e.response.json(), indent=2)}")
    except Exception as e:
        print(f"Error updating post {post_id}: {str(e)}")

@app.route('/test')
def test_page():
    import os
    return render_template('test.html', os=os)

@app.route('/test/post', methods=['POST'])
def test_post():
    page_id = request.form.get('page_id', os.getenv('FACEBOOK_DEFAULT_PAGE_ID'))
    access_token = request.form.get('access_token', os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN'))
    message = request.form.get('message')
    
    try:
        url = f'https://graph.facebook.com/{os.getenv("FACEBOOK_API_VERSION")}/{page_id}/feed'
        
        data = {
            'message': message,
            'access_token': access_token
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        formatted_response = json.dumps(response_data, indent=2)
        
        return render_template('test.html', response=formatted_response, os=os)
        
    except Exception as e:
        return render_template('test.html', response=str(e), os=os)
    
def make_request(json_data):
    request_data = json_data.get('request', {})
    metadata = json_data.get('metadata', {})
    
    # Validation des champs obligatoires
    if not request_data.get('url'):
        raise ValueError("URL is required in request")
    if not metadata.get('request_id'):
        raise ValueError("request_id is required in metadata")
    if not metadata.get('type'):
        raise ValueError("type is required in metadata")
    
    # Vérification du type
    if metadata.get('type') not in ['command', 'response', 'error']:
        raise ValueError("Invalid type in metadata. Must be 'command', 'response', or 'error'")
    
    # Préparation des paramètres de requête avec valeurs par défaut
    request_params = {
        'method': request_data.get('method', 'GET'),
        'url': request_data.get('url')
    }
    
    # Ajout optionnel des headers
    if 'headers' in request_data:
        request_params['headers'] = request_data['headers']
    
    # Ajout optionnel des query parameters
    if 'params' in request_data:
        request_params['params'] = request_data['params']
    
    # Ajout optionnel du body data
    if 'data' in request_data:
        if isinstance(request_data['data'], dict):
            request_params['json'] = request_data['data']  # Pour JSON
        else:
            request_params['data'] = request_data['data']  # Pour form-data ou raw
    
    # Exécution de la requête
    try:
        response = requests.request(**request_params)
        
        # Tentative de parser la réponse comme JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = response.text
        
        # Structure de la réponse
        response_structure = {
            "response": {
                "status": {
                    "code": response.status_code,
                    "reason": response.reason
                },
                "headers": dict(response.headers),
                "data": response_data,
                "timing": {
                    "elapsed": str(response.elapsed),
                    "timestamp": datetime.datetime.now().isoformat()
                }
            },
            "request": {
                "method": request_params['method'],
                "url": request_params['url']
            },
            "metadata": {
                "type": "response",
                "request_id": metadata['request_id'],
                "platform": metadata.get('platform', 'unknown'),
                "api_version": metadata.get('api_version', 'unknown'),
                "client_info": {
                    "type": "api_client",
                    "version": "1.0"
                }
            }
        }
        
        # Ajout optionnel des éléments de requête dans la réponse
        if 'headers' in request_params:
            response_structure['request']['headers'] = request_params['headers']
        if 'params' in request_params:
            response_structure['request']['params'] = request_params['params']
        if 'json' in request_params:
            response_structure['request']['data'] = request_params['json']
        elif 'data' in request_params:
            response_structure['request']['data'] = request_params['data']
        
        return response_structure
        
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs de requête
        error_structure = {
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            },
            "request": request_params,
            "metadata": {
                "type": "error",
                "request_id": metadata['request_id'],
                "platform": metadata.get('platform', 'unknown'),
                "api_version": metadata.get('api_version', 'unknown')
            }
        }
        return error_structure
    
@app.route('/webhook/history', methods=['GET'])
def webhook_history_endpoint():
    # Paramètres de pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Convertir deque en liste pour la pagination
    history_list = list(webhook_history)
    
    # Calculer les indices de pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Extraire la page demandée
    paginated_history = history_list[start_idx:end_idx]
    
    response_data = {
        'total': len(webhook_history),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(webhook_history) + per_page - 1) // per_page,
        'data': paginated_history
    }
    
    return json.dumps(response_data, indent=2), 200, {'Content-Type': 'application/json'}
    
def validate_message_structure(message_data):
    """Valide la structure du message et retourne (is_valid, error_message)"""
    if not isinstance(message_data, dict):
        return False, "Message must be a JSON object"
        
    # Vérification des champs obligatoires
    if 'request' not in message_data:
        return False, "Missing 'request' field"
        
    if 'metadata' not in message_data:
        return False, "Missing 'metadata' field"
        
    metadata = message_data.get('metadata', {})
    if not metadata.get('type'):
        return False, "Missing 'type' in metadata"
        
    if not metadata.get('request_id'):
        return False, "Missing 'request_id' in metadata"
        
    if metadata.get('type') not in ['command', 'response', 'error']:
        return False, "Invalid type in metadata. Must be 'command', 'response', or 'error'"
        
    # Pour une commande, on vérifie que c'est bien une nouvelle requête
    if metadata.get('type') == 'command':
        if 'response' in message_data or 'error' in message_data:
            return False, "Command message should not contain response or error"
            
    return True, None
    
if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'False'))