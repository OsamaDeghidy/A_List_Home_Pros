from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models import TimeStampedModel


class UserRole(models.TextChoices):
    CLIENT = 'client', _('Client')
    CONTRACTOR = 'contractor', _('A-List Home Pro')
    CREW = 'crew', _('Crew')
    SPECIALIST = 'specialist', _('Specialist')
    ADMIN = 'admin', _('Admin')


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
    )
    stripe_account_id = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return self.email


class EmailVerification(TimeStampedModel):
    """Model to store email verification tokens."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Email verification for {self.user.email}"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_contractor(self):
        return self.role == UserRole.CONTRACTOR

    @property
    def is_client(self):
        return self.role == UserRole.CLIENT
