from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, auth_utils
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def get_db():
    return next(models.get_db())

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        try:
            token = token.split(' ')[1]
            payload = auth_utils.jwt.decode(
                token, 
                auth_utils.SECRET_KEY, 
                algorithms=[auth_utils.ALGORITHM]
            )
            user_id = payload.get("sub")
        except:
            return jsonify({'message': 'Token invalide'}), 401
            
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Données manquantes'}), 400
        
    # Vérifier si l'utilisateur existe déjà
    if db.query(models.User).filter(models.User.email == data['email']).first():
        return jsonify({'message': 'Email déjà utilisé'}), 400
    
    # Créer le nouvel utilisateur
    hashed_password = auth_utils.get_password_hash(data['password'])
    new_user = models.User(
        email=data['email'],
        password=hashed_password,
        name=data.get('name')
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return jsonify({'message': 'Utilisateur créé avec succès'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Données manquantes'}), 400
    
    user = db.query(models.User).filter(models.User.email == data['email']).first()
    
    if not user or not auth_utils.verify_password(data['password'], user.password):
        return jsonify({'message': 'Email ou mot de passe incorrect'}), 401
    
    access_token = auth_utils.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    token = request.headers.get('Authorization').split(' ')[1]
    try:
        payload = auth_utils.jwt.decode(
            token, 
            auth_utils.SECRET_KEY, 
            algorithms=[auth_utils.ALGORITHM]
        )
        user_id = payload.get("sub")
        
        db = get_db()
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404
            
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'emailVerified': user.emailVerified,
            'image': user.image
        })
    except:
        return jsonify({'message': 'Token invalide'}), 401 