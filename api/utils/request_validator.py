from datetime import datetime
import uuid

def create_metadata(request_type="command", platform="web", source=None):
    """Crée des métadonnées standardisées pour les requêtes"""
    return {
        "type": request_type,
        "request_id": str(uuid.uuid4()),
        "platform": platform,
        "api_version": "v1",
        "source": source or "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

def format_error_response(error, request_data=None, metadata=None):
    """Formate une réponse d'erreur standardisée"""
    return {
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        },
        "request": request_data,
        "metadata": metadata or create_metadata(request_type="error")
    } 