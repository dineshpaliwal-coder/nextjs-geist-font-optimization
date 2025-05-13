from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_login_failed
from .models import User, LoginAttempt, UserRole
import uuid

@receiver(pre_save, sender=User)
def handle_password_change(sender, instance, **kwargs):
    """
    Track when a user's password is changed.
    """
    if instance.pk:  # Only for existing users
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.password != instance.password:
                instance.password_changed_at = timezone.now()
                instance.force_password_change = False
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def create_user_api_key(sender, instance, created, **kwargs):
    """
    Generate API key for new users.
    """
    if created and not instance.api_key:
        instance.api_key = uuid.uuid4()
        instance.save(update_fields=['api_key'])

@receiver(user_logged_in)
def track_successful_login(sender, request, user, **kwargs):
    """
    Track successful login attempts.
    """
    if request:
        LoginAttempt.objects.create(
            user=user,
            email=user.email,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            successful=True
        )
        
        # Update user's last login IP and active timestamp
        user.last_login_ip = get_client_ip(request)
        user.last_active = timezone.now()
        user.save(update_fields=['last_login_ip', 'last_active'])

@receiver(user_login_failed)
def track_failed_login(sender, credentials, request, **kwargs):
    """
    Track failed login attempts.
    """
    if request:
        LoginAttempt.objects.create(
            email=credentials.get('email', ''),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            successful=False,
            failure_reason=kwargs.get('error_message', 'Unknown error')
        )

@receiver(post_save, sender=UserRole)
def handle_role_assignment(sender, instance, created, **kwargs):
    """
    Handle role assignment updates.
    """
    if created:
        # You might want to send notifications or perform other actions
        # when a role is assigned to a user
        pass
    elif instance.expires_at and instance.expires_at <= timezone.now():
        # Automatically deactivate expired roles
        instance.is_active = False
        instance.save(update_fields=['is_active'])

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
