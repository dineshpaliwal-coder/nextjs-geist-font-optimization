from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # Core App URLs
    path('', include('apps.marketing.urls')),  # Marketing pages (public website)
    
    # Authentication URLs
    path('accounts/', include('apps.accounts.urls')),
    
    # Main Application URLs
    path('dashboard/', include('apps.dashboard.urls')),
    path('crm/', include('apps.crm.urls')),
    path('projects/', include('apps.projects.urls')),
    # Commented out hrm urls due to missing module to fix import error
    # path('hr/', include('apps.hrm.urls')),
    # Commented out billing urls due to missing module to fix import error
    # path('billing/', include('apps.billing.urls')),
    # Commented out support urls due to missing module to fix import error
    # path('support/', include('apps.support.urls')),
    # Commented out affiliate urls due to missing module to fix import error
    # path('affiliate/', include('apps.affiliate.urls')),
    
    # API URLs
    # Commented out crm api urls due to missing module to fix import error
    # path('api/v1/crm/', include('apps.crm.api.urls')),
    # Commented out projects api urls due to missing module to fix import error
    # path('api/v1/projects/', include('apps.projects.api.urls')),
    # Commented out hrm api urls due to missing module to fix import error
    # path('api/v1/hr/', include('apps.hrm.api.urls')),
    # Commented out billing api urls due to missing module to fix import error
    # path('api/v1/billing/', include('apps.billing.api.urls')),
    # Commented out support api urls due to missing module to fix import error
    # path('api/v1/support/', include('apps.support.api.urls')),
    # Commented out affiliate api urls due to missing module to fix import error
    # path('api/v1/affiliate/', include('apps.affiliate.api.urls')),
    
    # Stripe Webhook
    # Commented out billing webhook urls due to missing module to fix import error
    # path('webhook/stripe/', include('apps.billing.webhooks.urls')),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers - commented out due to missing apps.core.views module
# handler400 = 'apps.core.views.error_400'  # Bad request
# handler403 = 'apps.core.views.error_403'  # Permission denied
# handler404 = 'apps.core.views.error_404'  # Page not found
# handler500 = 'apps.core.views.error_500'  # Server error
