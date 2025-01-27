from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def generate_confirmation_token(email):
    try:
        serializer=URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token=serializer.dumps(email, salt='email-confirm-salt')
        logger.debug(f"Token oluşturuldu: {email}")
        return token
    except Exception as e:
        logger.error(f"Token oluşturma hata: {e}")
        return None

def confirm_token(token, expiration=3600):
    try:
        serializer=URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email=serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
        logger.debug(f"Token doğrulandı: {email}")
        return email
    except SignatureExpired:
        logger.warning("Token süresi doldu.")
        return False
    except BadSignature:
        logger.warning("Token geçersiz.")
        return False
    except Exception as e:
        logger.error(f"Token doğrulama hata: {e}")
        return False
