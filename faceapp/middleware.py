# faceapp/middleware.py
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from .models import User, APIToken
from .auth import decode_token

class JWTAuthenticationMiddleware:
    """
    Middleware that reads Authorization: Bearer <token>
    If token present and valid -> sets request.user to User instance.
    If token present but invalid/expired -> returns 401.
    If no token -> request.user stays None (so public endpoints remain accessible).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Do not override request.user here — leave Django's
        # AuthenticationMiddleware to populate it (AnonymousUser or auth user).
        # Only set request.user when a valid Bearer token is provided.

        auth = None
        # Django request.headers available in modern Django
        try:
            auth = request.headers.get("Authorization")
        except Exception:
            # Fallback for older Django versions
            auth = request.META.get("HTTP_AUTHORIZATION")

        # Only attempt JWT auth for API endpoints to avoid interfering
        # with Django admin and regular session authentication.
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        if auth:
            parts = auth.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                try:
                    payload = decode_token(token)
                except jwt.ExpiredSignatureError:
                    return JsonResponse({"error": "Token expired"}, status=401)
                except jwt.InvalidTokenError:
                    return JsonResponse({"error": "Invalid token"}, status=401)
                except Exception:
                    return JsonResponse({"error": "Invalid token"}, status=401)

                # Load user
                try:
                    user = User.objects.get(id=payload.get("user_id"))
                    # Check server-side token store for revocation/expiry
                    token_obj = APIToken.objects.filter(key=token).first()
                    if token_obj and not token_obj.is_valid():
                        return JsonResponse({"error": "Token revoked or expired"}, status=401)

                    # If token not found in DB, treat as invalid (optional)
                    if token_obj is None:
                        return JsonResponse({"error": "Token not recognized"}, status=401)

                    request.user = user
                except User.DoesNotExist:
                    return JsonResponse({"error": "User not found"}, status=401)
            else:
                # If Authorization header exists but not Bearer format -> reject
                return JsonResponse({"error": "Invalid Authorization header format"}, status=401)

        # Continue to view
        response = self.get_response(request)
        return response
