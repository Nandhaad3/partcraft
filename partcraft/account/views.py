from django.db.migrations import serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from .serializers import *
from . emails import *
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}

class UserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_via_email(serializer.data['email'])
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                em=request.data['email']
                print(em)
                response = Response({"status": "success","OTP":'SEND SUCCESSFULLY', "message": "User registered successfully", 'data': serializer.data }, status=status.HTTP_201_CREATED)
                response.set_cookie('email', str(em), httponly=True, secure=True,
                                    max_age=3600, samesite='None')
                return response

        return Response({"status": "error", "message": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    def post(self, request):
        cookies_email=request.COOKIES.get('email')
        print(cookies_email)
        datas = request.data.copy()
        datas['email']=cookies_email
        datas['otp']=request.data.get('otp')
        serializer = VerifyEmailSerializer(data=datas)
        # serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp = serializer.data['otp']
            email = serializer.data['email']
            try:
                user = User.objects.get(email=email, otp=otp)
            except ObjectDoesNotExist:
                return Response({"status": "error", "message": "Invalid OTP", 'data': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            response = Response({"status": "success", "message": "OTP verified successfully", "email": user.email}, status=status.HTTP_200_OK)
            response.delete_cookie('email')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(request=request, email=email, password=password)
            if user:
                if user.check_password(password):
                    token = get_token_for_user(user)
                    response = Response({"status": "success", "message": "User Login Successfully", "username": user.email, "full name":user.name, "token": token}, status=status.HTTP_200_OK)
                    response.set_cookie('refresh_token', str(token.get('refresh')), httponly=True, secure=True, max_age=3600, samesite='None')
                    return response
                else:
                    return Response({"status": "error", "message": "Password has been changed. Please login with the new password"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"status": "error", "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class UserChangePasswordView(APIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_session_auth_hash(request, request.user)
            return Response({"status": "success", "message": "Password Changed Successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Password reset failed. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetEmailView(APIView):
    serializer_class = SendPasswordResetEmailSerializer
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"status": "success", "message": "Password reset email has been sent successfully. Please check your email inbox. or some check spam"}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Password reset failed. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer
    def post(self, request, uid, token, *args, **kwargs):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid(raise_exception=True):
            return Response({"status": "success", "message": "Password Changed Successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "error", "message": "Password reset link has expired. Please request a new link or Invalid Link"}, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response =  Response({"status": "success", "message": "User Logout Successfully"}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)