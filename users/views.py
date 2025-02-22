from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, timedelta
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from . import serializers
from . import models
import random
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string




class CustomAuthToken(ObtainAuthToken):
    serializer_class = serializers.CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
        })


# Create User Account
@api_view(['POST'])
def user_register(request):
    serializer = serializers.RegisterationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        username_existance = models.CustomUser.objects.filter(username=username).exists()
        email_existance = models.CustomUser.objects.filter(email=email).exists()


        if username_existance:
            return Response({"Message":"This username is already exists!"}, status=status.HTTP_400_BAD_REQUEST)
        elif email_existance:
            return Response({"Message":"This email is already exists!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = models.CustomUser.objects.create(
                    email = email,
                    username = username,
                )
                user.set_password(password)  # Hash the password
                user.save()

                token,_ = Token.objects.get_or_create(user=user)

                return Response({
                    "message": "User created successfully",
                    "token": token.key
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# OTP Processes
# 1- Generate a random otp code
def generate_otp():
    return random.randint(100000, 999999)  # 6-digit OTP

# 2- Prepare the function that will be called later to send an email
def custom_send_mail(email, subject, message):
    subject = subject
    message = message
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)



# 3- Send an otp using the email to be used for login if the user is not logged in, if not send otp
@api_view(['POST'])
def request_otp(request):
    # Check if the user is already logged in
    if request.user.is_authenticated:
        return Response({'message': 'You are already logged in. No OTP required.'}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        if 'email' in request.data:
            email = request.data['email']
            try:
                user = models.CustomUser.objects.get(email=email)
                otp = generate_otp()
                models.OTP.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=now() + timedelta(minutes=15)  # OTP valid for 10 minutes
                )

                subject = "Your Login OTP"
                message = f"Your OTP for login is {otp}. It is valid for 5 minutes."
                custom_send_mail(email, subject, message)
                return Response({'message': 'OTP sent successfully to your email'}, status=status.HTTP_200_OK)
            except models.CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response({'Message': 'Email is required!'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




# 4- Login usgin the otp code that sended to your email
@api_view(['POST'])
def user_login_with_otp(request):
    if request.method == 'POST':
        if 'email' in request.data and 'otp' in request.data:
            email = request.data['email']
            otp_value = request.data['otp']
            try:
                user = models.CustomUser.objects.get(email=email)
                otp = models.OTP.objects.filter(user=user, otp=otp_value).first()
                if otp and otp.is_valid():
                    # OTP is valid
                    otp.delete()  # Remove the OTP after successful verification
                    # Get or create the auth token for the user
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'message': 'OTP verified successfully',
                    }, status=200)
                else:
                    return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except models.CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({'Message': 'Email and OTP code are required!'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        user_data = {
            "user": request.user.username,
            "email": request.user.email
        }
        return Response(user_data, status=status.HTTP_200_OK)
    elif request.method == 'PUT':

        serializer = serializers.UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context={'request': request}  # Add this line
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"Message: " : "Profile Info Updated Successfully", "User Info" : serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# Reset password
@api_view(['POST'])
def password_reset_request(request):
    if request.method == "POST":
        if 'email' in request.data:
            email = request.data['email']
            user_existance = models.CustomUser.objects.filter(email=email).exists()
            if user_existance:
                user = models.CustomUser.objects.get(email=email)
                uid = urlsafe_base64_encode(str(user.pk).encode('utf-8'))
                token = default_token_generator.make_token(user)

                reset_link = f"{get_current_site(request).domain}/reset/{uid}/{token}/"
                email_subject = "Password Reset Request"
                email_message = f"Hi, {user}, To reset your password, please, follow this link {reset_link}"
                custom_send_mail(email, email_subject, email_message)
                return Response({'message': 'Password reset link sent to email.'}, status=status.HTTP_200_OK)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Message: " : "Email field is required!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)




@api_view(['POST'])
def password_reset_confirm(request, uidb64, token):
    try:
        # Decode UID
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = models.CustomUser.objects.get(pk=uid)

        # Validate token
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate new password
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
    except models.CustomUser.DoesNotExist:
        return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def password_change(request):
    user = request.user
    if 'current_password' in request.data and 'new_password' in request.data:
        current_password = request.data['current_password']
        new_password = request.data['new_password']

        # Check if current password is correct
        if not user.check_password(current_password):
            return Response({"Error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        # Update the password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
    return Response({"Error: " : "The current password and the new password are required!"}, status=status.HTTP_400_BAD_REQUEST)

    
