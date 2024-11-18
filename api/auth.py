from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, auth_utils
from functools import wraps
import datetime
import re
from api.validators import validate_phone

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
            
            db = get_db()
            current_user = db.query(models.User).filter(models.User.id == user_id).first()
            
            if not current_user:
                return jsonify({'message': 'Utilisateur non trouvé'}), 404
                
        except:
            return jsonify({'message': 'Token invalide'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    db = get_db()
    
    if not all(key in data for key in ['name', 'phone', 'password']):
        return jsonify({'message': 'Données manquantes'}), 400
    
    # Nettoyage et validation du numéro de téléphone
    phone = data['phone'].replace(' ', '')
    if not validate_phone(phone):
        return jsonify({'message': 'Format de numéro de téléphone invalide'}), 400
    
    # Vérification si le numéro existe déjà
    if db.query(models.User).filter(models.User.phone == phone).first():
        return jsonify({'message': 'Ce numéro de téléphone est déjà utilisé'}), 400
    
    # Création du nouvel utilisateur
    hashed_password = auth_utils.get_password_hash(data['password'])
    new_user = models.User(
        name=data['name'],
        phone=phone,
        password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        return jsonify({'message': 'Inscription réussie'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'message': 'Erreur lors de l\'inscription'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()
    
    if not data or not data.get('phone') or not data.get('password'):
        return jsonify({'message': 'Données manquantes'}), 400
    
    # Nettoyage du numéro de téléphone
    phone = data['phone'].replace(' ', '')
    
    user = db.query(models.User).filter(models.User.phone == phone).first()
    
    if not user or not auth_utils.verify_password(data['password'], user.password):
        return jsonify({'message': 'Numéro de téléphone ou mot de passe incorrect'}), 401
    
    access_token = auth_utils.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'name': user.name,
            'phone': user.phone
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Déconnexion réussie'}), 200 

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'phone': current_user.phone,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'updated_at': current_user.updated_at.isoformat() if current_user.updated_at else None
    })