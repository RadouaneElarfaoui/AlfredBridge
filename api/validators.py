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