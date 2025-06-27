from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated


from .models import EmailOTP, ChatMessage
from .validators import SignupSerializer, LoginSerializer
from .utils.utilities import generate_otp, send_otp_email

User = get_user_model()


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            res = Response({"success": True})
            res.set_cookie("access", str(refresh.access_token), httponly=True)
            res.set_cookie("refresh", str(refresh), httponly=True)
            return res

        return Response(serializer.errors, status=400)

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = User.objects.create_user(email=email, password=password, is_active=False)
            user.save()
            
            otp = generate_otp()
            EmailOTP.objects.create(user=user, otp=otp)
            send_otp_email(email, otp)

        return Response({
            "success": True,
            "message": "OTP send to email."
        })


class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), "your-google-client-id.apps.googleusercontent.com")
            email = idinfo["email"]
            name = idinfo.get("name", "")
            user, created = User.objects.get_or_create(email=email, defaults={"username": email.split('@')[0]})
            refresh = RefreshToken.for_user(user)
            res = Response({'success': True})
            res.set_cookie('access', str(refresh.access_token), httponly=True)
            res.set_cookie('refresh', str(refresh), httponly=True)
            return res
        except Exception as e:
            return Response({'error': 'Invalid Google token'}, status=400)

class SignupVerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)

            if otp_obj.is_expired():
                otp_obj.delete()
                return Response({"error": "OTP expired, request a new one"}, status=400)

            if otp_obj.otp == otp_input:
                user.is_active = True
                user.save()
                otp_obj.delete()

                refresh = RefreshToken.for_user(user)
                res = Response({
                    "success": True, 
                    "message":"Account Verified!"
                    })
                res.set_cookie("access", str(refresh.access_token), httponly=True)
                res.set_cookie("refresh", str(refresh), httponly=True)
                return res
            else:
                return Response({"error": "Invalid OTP"}, status=400)
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except EmailOTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=404)

class ForgotPasswordRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
            EmailOTP.objects.filter(user=user).delete()
            otp = generate_otp()
            EmailOTP.objects.create(user=user, otp=otp)
            send_otp_email(email, otp)
            return Response({"success": True, "message": "OTP sent to email"})
        except User.DoesNotExist:
            return Response({"error": "No user found with this email"}, status=404)
        
class ForgotPasswordVerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.get(user=user)

            if otp_obj.is_expired():
                otp_obj.delete()
                return Response({"error": "OTP expired, request a new one"}, status=400)

            if otp_obj.otp != otp_input:
                return Response({"error": "Invalid OTP"}, status=400)
            
            return Response({"success": True, "message": "OTP verified"})

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except EmailOTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=404)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        try:
            user = User.objects.get(email=email)
            if(new_password == confirm_password):
                user.set_password(new_password)
                user.save()
                EmailOTP.objects.filter(user=user).delete() 
                return Response({"success": True, "message": "Password reset successfully"})
            else:
                return Response({"error": "Passwords do not match"}, status=400)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, room_id):
        # Pagination params
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("limit", 20))
        offset = (page - 1) * page_size

        # Filter messages for the room, latest first
        messages_qs = ChatMessage.objects.filter(room_id=room_id).order_by("-timestamp")
        total = messages_qs.count()

        # Paginating
        messages = messages_qs[offset:offset + page_size]

        # Response
        data = [
            {
                "user": msg.user,
                "message": msg.message,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]

        return Response({
            "messages": data,
            "total": total,
            "page": page,
            "limit": page_size
        })