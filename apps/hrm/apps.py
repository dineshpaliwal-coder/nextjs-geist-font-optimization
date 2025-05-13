from django.apps import AppConfig

class HrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hrm'
    verbose_name = 'Human Resources'

    def ready(self):
        pass
