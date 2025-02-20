from rest_framework import serializers
from django.contrib.auth import authenticate
from . import models


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.", code='authorization')
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.", code='authorization')

        attrs['user'] = user
        return attrs



class RegisterationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = models.CustomUser
        fields = ['email', 'username', 'password']



class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)

    class Meta:
        model = models.CustomUser
        fields = ['email', 'username']





# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)
    

