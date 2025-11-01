from django.db import models

# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('authority', 'Municipal Authority'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"