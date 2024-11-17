from api.models import init_db, get_db, User
from sqlalchemy import text
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        # Test 1: Initialisation de la base de données
        logger.info("Test 1: Initialisation de la base de données...")
        init_db()
        
        # Test 2: Connexion et requête simple
        logger.info("Test 2: Test de connexion simple...")
        db = next(get_db())
        result = db.execute(text("SELECT 1")).scalar()
        logger.info(f"Résultat de la requête test: {result}")
        
        # Test 3: Création d'un utilisateur test
        logger.info("Test 3: Création d'un utilisateur test...")
        test_user = User(
            email="test@example.com",
            password="test_password",
            name="Test User"
        )
        
        db.add(test_user)
        db.commit()
        logger.info("Utilisateur test créé avec succès!")
        
        # Test 4: Lecture de l'utilisateur
        logger.info("Test 4: Lecture de l'utilisateur...")
        user = db.query(User).filter(User.email == "test@example.com").first()
        logger.info(f"Utilisateur trouvé: {user.email}")
        
        # Nettoyage
        logger.info("Nettoyage de la base de données...")
        db.delete(user)
        db.commit()
        
        logger.info("Tous les tests ont réussi!")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors des tests: {str(e)}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_connection() 