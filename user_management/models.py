import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager  # # A new class is imported. ##
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
import jwt
import time

# Create your models here.

# Keep Superuser Model separated from end user models.
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """User model."""
    # cannot use username, as we are overriding username for user authentication with email
    username = None
    full_name = models.CharField(_("Full Name"), max_length=200, default="None")
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=12, null=False, unique=True)
    user_registered = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()


class Nursery(models.Model):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    RATINGS_CHOICES = [
        (ONE, 1),
        (TWO, 2),
        (THREE, 3),
        (FOUR, 4),
        (FIVE, 5),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    email = models.EmailField(_("Email"), max_length=254, unique=True)
    password = models.TextField(_("password"), blank=False, null=False)
    name = models.CharField(_("Nursery Name"), max_length=100, blank=False, null=False)
    about = models.TextField(_("About"))
    isdeleted = models.BooleanField(_("User deleted"), default=False)
    ratings = models.CharField(max_length=10, choices=RATINGS_CHOICES, default=ONE)
    IsNursery = models.BooleanField(default=True, editable=False)
    isdeleted = models.BooleanField(_("User deleted"), default=False, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("EndUser - Nursery")
        verbose_name_plural = _("EndUser - Nursery")


class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    email = models.EmailField(_("Email"), max_length=254, unique=True)
    password = models.CharField(_("password"), max_length=128, blank=False, null=False)
    first_name = models.CharField(_("First Name"), max_length=100, blank=False, null=False)
    middle_name = models.CharField(_("Middle Name"), max_length=100, blank=True, null=True, default="")
    last_name = models.TextField(_("Last Name"), max_length=100, blank=True, null=True, default="")
    IsBuyer = models.BooleanField(default=True, editable=False)
    isdeleted = models.BooleanField(_("User deleted"), default=False, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)

    def get_full_name(self):
        return f"{self.first_name}  {self.middle_name}   {self.last_name}"

    def get_first_name(self):
        return f"{self.first_name}"

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("EndUser - Buyer")
        verbose_name_plural = _("EndUser - Buyer")