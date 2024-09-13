from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Cost_Code(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if password != password2:
            raise ValueError('Passwords must match')
        user = self.model(email=self.normalize_email(email), name=name, tc=tc, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None, password2=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, tc, password, password2=password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    name = models.CharField(verbose_name="Name", max_length=255)
    tc = models.BooleanField()
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(verbose_name="OTP", max_length=255, blank=True)
    cost_type = models.ForeignKey(Cost_Code, on_delete=models.CASCADE, default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Changed from property to field
    is_superuser = models.BooleanField(default=False)  # Changed from property to field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edit = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_post = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

