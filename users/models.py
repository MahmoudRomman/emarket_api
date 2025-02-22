from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now, timedelta
from django.conf import settings
from django.db.models.signals import post_save



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} - {self.email}"


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)  # Example field

    def __str__(self):
        return self.user.username


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otps")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if the OTP is still valid."""
        return now() < self.expires_at
