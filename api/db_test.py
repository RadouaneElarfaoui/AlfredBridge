from models import init_db, get_db

def test_connection():
    try:
        # Tester la création des tables
        init_db()
        
        # Tester la connexion avec une requête simple
        db = next(get_db())
        db.execute("SELECT 1")
        print("Connexion à la base de données réussie!")
        
    except Exception as e:
        print(f"Erreur de connexion: {e}")
    
if __name__ == "__main__":
    test_connection() 