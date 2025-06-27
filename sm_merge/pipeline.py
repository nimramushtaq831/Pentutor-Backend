from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

def generate_jwt_tokens(backend, user, response, *args, **kwargs):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Send JWTs as cookies
    res = JsonResponse({'message': 'Login successful'})
    res.set_cookie('access', access_token, httponly=True)
    res.set_cookie('refresh', refresh_token, httponly=True)
    return res
