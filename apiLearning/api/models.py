from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email), username=username, password=password, **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email


class Subject(models.Model):
    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll = models.IntegerField(default=0)
    subjects = models.ManyToManyField(Subject, related_name="students")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject, related_name="teachers")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
