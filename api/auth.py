from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, auth_utils
from functools import wraps
import datetime
import re

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
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug: Print the received data

        db = get_db()
        
        # Validation des données
        if not all(key in data for key in ['email', 'password', 'name']):
            print("Données manquantes")  # Debug: Print missing data error
            return jsonify({'message': 'Données manquantes'}), 400
            
        # Validation du format email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            print("Format d'email invalide")  # Debug: Print invalid email format
            return jsonify({'message': 'Format d\'email invalide'}), 400
            
        # Validation du mot de passe
        if len(data['password']) < 8:
            print("Mot de passe trop court")  # Debug: Print password too short
            return jsonify({'message': 'Le mot de passe doit contenir au moins 8 caractères'}), 400
        
        if not re.search(r'[A-Z]', data['password']):
            print("Mot de passe sans majuscule")  # Debug: Print password missing uppercase
            return jsonify({'message': 'Le mot de passe doit contenir au moins une majuscule'}), 400
            
        if not re.search(r'[a-z]', data['password']):
            print("Mot de passe sans minuscule")  # Debug: Print password missing lowercase
            return jsonify({'message': 'Le mot de passe doit contenir au moins une minuscule'}), 400
            
        if not re.search(r'\d', data['password']):
            print("Mot de passe sans chiffre")  # Debug: Print password missing digit
            return jsonify({'message': 'Le mot de passe doit contenir au moins un chiffre'}), 400
        
        # Vérifier si l'email existe déjà
        if db.query(models.User).filter(models.User.email == data['email']).first():
            print("Email déjà utilisé")  # Debug: Print email already used
            return jsonify({'message': 'Cet email est déjà utilisé'}), 400
        
        try:
            # Créer le nouvel utilisateur
            hashed_password = auth_utils.get_password_hash(data['password'])
            print("Hashed password:", hashed_password)  # Debug: Print hashed password

            new_user = models.User(
                email=data['email'],
                password=hashed_password,
                name=data['name'],
                created_at=datetime.datetime.now(datetime.UTC)
            )
            
            db.add(new_user)
            db.commit()
            
            print("Inscription réussie!")  # Debug: Print success message
            return jsonify({
                'message': 'Inscription réussie!',
                'user_id': new_user.id
            }), 201
            
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'inscription: {str(e)}")  # Debug: Print exception message
            return jsonify({'message': 'Erreur lors de l\'inscription'}), 500
            
    except Exception as e:
        print(f"Erreur générale: {str(e)}")  # Debug: Print general exception message
        return jsonify({'message': 'Erreur serveur'}), 500

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

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'message': 'Déconnexion réussie'}), 200 

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name
    })