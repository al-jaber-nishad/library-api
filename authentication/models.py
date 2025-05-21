from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField
from utils.mixins import BaseModel


class Role(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, username='', first_name='', last_name='', gender='male', password=None, **kwargs):
        if not email:
            raise ValueError('User must have an email address')
            
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name= first_name,
            last_name = last_name,
            gender = gender,
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username='', first_name='', last_name='', gender='male', password=None, **kwargs):
        user = self.create_user(
            email= email,
            username=username,
            first_name= first_name,
            last_name = last_name,
            gender = gender,
            password=password,
            **kwargs,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHERS = 'others', _('Others')
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('admin')
        EMPLOYEE = 'employee', _('employee')
        CUSTOMER = 'customer', _('customer')
        VENDOR = 'vendor', _('vendor')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)

    country_code = models.CharField(max_length=20, null=True, blank=True)
    primary_phone = PhoneNumberField(verbose_name='phone number', unique=True, null=True, blank=True)
    secondary_phone = PhoneNumberField(unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    email_token = models.CharField(max_length=500, null=True, blank=True)
    phone_otp = models.CharField(max_length=100, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    penalty_points = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'gender']

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return f"<{self.id}>: {self.email if self.email else str(self.username)}"

    def save(self, *args, **kwargs):
        self.username = self.username.replace(' ', '_').lower() if self.username else ''
        super().save(*args, **kwargs)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin
