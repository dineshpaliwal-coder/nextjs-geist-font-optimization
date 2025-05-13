from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Tenant, Domain, TenantSettings
import stripe

@receiver(post_save, sender=Tenant)
def create_tenant_settings(sender, instance, created, **kwargs):
    """
    Create TenantSettings when a new Tenant is created
    """
    if created:
        TenantSettings.objects.create(tenant=instance)

@receiver(post_save, sender=Tenant)
def setup_stripe_customer(sender, instance, created, **kwargs):
    """
    Create or update Stripe customer when a Tenant is saved
    """
    if settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            if created and not instance.stripe_customer_id:
                # Create new Stripe customer
                customer = stripe.Customer.create(
                    email=instance.email,
                    name=instance.name,
                    metadata={
                        'tenant_id': str(instance.id),
                        'subscription_plan': instance.subscription_plan
                    }
                )
                # Update tenant with Stripe customer ID
                Tenant.objects.filter(id=instance.id).update(
                    stripe_customer_id=customer.id
                )
            elif instance.stripe_customer_id:
                # Update existing Stripe customer
                stripe.Customer.modify(
                    instance.stripe_customer_id,
                    email=instance.email,
                    name=instance.name,
                    metadata={
                        'tenant_id': str(instance.id),
                        'subscription_plan': instance.subscription_plan
                    }
                )
        except stripe.error.StripeError as e:
            # Log the error but don't prevent tenant creation/update
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Stripe error for tenant {instance.id}: {str(e)}")

@receiver(post_delete, sender=Tenant)
def cleanup_stripe_customer(sender, instance, **kwargs):
    """
    Clean up Stripe customer when a Tenant is deleted
    """
    if settings.STRIPE_SECRET_KEY and instance.stripe_customer_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe.Customer.delete(instance.stripe_customer_id)
        except stripe.error.StripeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting Stripe customer {instance.stripe_customer_id}: {str(e)}")

@receiver(post_save, sender=Domain)
def handle_primary_domain(sender, instance, created, **kwargs):
    """
    Ensure there's always one primary domain per tenant
    """
    if created and not instance.is_primary:
        # If this is the first domain for the tenant, make it primary
        if not Domain.objects.filter(tenant=instance.tenant).exclude(id=instance.id).exists():
            Domain.objects.filter(id=instance.id).update(is_primary=True)
    elif instance.is_primary:
        # Ensure no other domains for this tenant are primary
        Domain.objects.filter(
            tenant=instance.tenant,
            is_primary=True
        ).exclude(id=instance.id).update(is_primary=False)

@receiver(post_delete, sender=Domain)
def handle_domain_deletion(sender, instance, **kwargs):
    """
    If the primary domain is deleted, make another domain primary
    """
    if instance.is_primary:
        # Try to set another domain as primary
        next_domain = Domain.objects.filter(
            tenant=instance.tenant
        ).first()
        if next_domain:
            next_domain.is_primary = True
            next_domain.save()
