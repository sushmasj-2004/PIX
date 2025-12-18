# faceapp/auth.py
import jwt
import datetime
from django.conf import settings
from .models import User

# Token lifetime (hours)
ACCESS_TOKEN_HOURS = 24

def create_token(user):
    """
    Create a JWT for the given user.
    Contains user_id and email, expires in ACCESS_TOKEN_HOURS.
    """
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(hours=ACCESS_TOKEN_HOURS)
    payload = {
        "user_id": user.id,
        "email": getattr(user, "email", None),
        "iat": now,
        "exp": exp
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    # PyJWT >= 2.x returns a str; older returns bytes — ensure str
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token):
    """
    Decode token and return payload (or raise jwt exceptions).
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return payload
