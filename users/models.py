from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('employee', 'Employee'),
        ('director', 'Director'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='employee')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def is_director(self):
        return self.user_type == 'director'
        
    def is_employee(self):
        return self.user_type == 'employee'
