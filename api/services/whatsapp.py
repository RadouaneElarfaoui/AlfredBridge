import requests
import os
import random
import string
from datetime import datetime, timedelta

class WhatsAppService:
    def __init__(self):
        self.base_url = "https://7103.api.greenapi.com/waInstance7103864851"
        self.token = "75385fbb3408429f96f0f7df457687b8ef9927e14a0d4cacb7"
        
    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=6))
        
    def send_verification_code(self, phone_number, code):
        url = f"{self.base_url}/sendMessage/{self.token}"
        
        # Formater le message
        message = (
            f"Votre code de vérification AlfredBridge est : *{code}*\n\n"
            "Ce code expire dans 10 minutes.\n"
            "Ne le partagez avec personne."
        )
        
        # Formater le numéro pour WhatsApp
        wa_phone = phone_number.replace('+', '') + '@c.us'
        
        payload = {
            "chatId": wa_phone,
            "message": message
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur WhatsApp: {str(e)}")
            return False 