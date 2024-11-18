from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, auth_utils
from functools import wraps
import datetime
import re
from api.validators import validate_phone
from api.services.whatsapp import WhatsAppService
from uuid import UUID

auth_bp = Blueprint('auth', __name__)
whatsapp_service = WhatsAppService()

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

@auth_bp.route('/send-verification', methods=['POST'])
@token_required
def send_verification(current_user):
    if current_user.is_phone_verified:
        return jsonify({'message': 'Numéro déjà vérifié'}), 400
        
    # Générer un nouveau code
    code = whatsapp_service.generate_verification_code()
    expiration = datetime.utcnow() + timedelta(minutes=10)
    
    # Mettre à jour l'utilisateur
    db = get_db()
    current_user.verification_code = code
    current_user.verification_code_expires = expiration
    db.commit()
    
    # Envoyer le code par WhatsApp
    success = whatsapp_service.send_verification_code(current_user.phone, code)
    
    if success:
        return jsonify({'message': 'Code de vérification envoyé'}), 200
    return jsonify({'message': 'Erreur lors de l\'envoi du code'}), 500

@auth_bp.route('/verify-phone', methods=['POST'])
@token_required
def verify_phone(current_user):
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'message': 'Code requis'}), 400
        
    if current_user.is_phone_verified:
        return jsonify({'message': 'Numéro déjà vérifié'}), 400
        
    if (not current_user.verification_code or 
        not current_user.verification_code_expires or 
        datetime.utcnow() > current_user.verification_code_expires):
        return jsonify({'message': 'Code expiré'}), 400
        
    if code != current_user.verification_code:
        return jsonify({'message': 'Code incorrect'}), 400
        
    # Valider le numéro
    db = get_db()
    current_user.is_phone_verified = True
    current_user.verification_code = None
    current_user.verification_code_expires = None
    db.commit()
    
    return jsonify({'message': 'Numéro vérifié avec succès'}), 200