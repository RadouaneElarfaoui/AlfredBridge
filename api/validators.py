import re

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
        
    return True, None 

PHONE_PATTERNS = {
    '+212': r'^\+212[67][0-9]{8}$',  # Maroc
    '+33': r'^\+33[67][0-9]{8}$',    # France
    '+1': r'^\+1[2-9][0-9]{9}$',     # USA/Canada
    '+44': r'^\+44[7][0-9]{9}$',     # UK
    '+49': r'^\+49[15][0-9]{9,10}$', # Allemagne
    'default': r'^\+[1-9][0-9]{6,14}$'
}

def validate_phone(phone):
    """Valide le format du numéro de téléphone selon le pays"""
    phone = phone.strip()
    if not phone.startswith('+'):
        return False
        
    # Trouver le bon pattern selon le préfixe pays
    for prefix, pattern in PHONE_PATTERNS.items():
        if phone.startswith(prefix):
            return bool(re.match(pattern, phone))
            
    return bool(re.match(PHONE_PATTERNS['default'], phone)) 