from django.apps import AppConfig

class AffiliateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.affiliate'
    verbose_name = 'Affiliate Program'

    def ready(self):
        pass
