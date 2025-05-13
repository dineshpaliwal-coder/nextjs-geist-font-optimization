from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import User, Role, UserRole, LoginAttempt

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'get_full_name', 'tenant', 'is_active', 
                   'is_tenant_admin', 'last_login', 'date_joined')
    list_filter = ('is_active', 'is_tenant_admin', 'tenant', 'date_joined', 
                  'two_factor_enabled')
    search_fields = ('email', 'first_name', 'last_name', 'tenant__name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone', 'job_title', 'department')
        }),
        (_('Tenant'), {
            'fields': ('tenant', 'is_tenant_admin')
        }),
        (_('Security'), {
            'fields': ('two_factor_enabled', 'force_password_change', 
                      'api_access_enabled', 'api_key')
        }),
        (_('Preferences'), {
            'fields': ('language', 'timezone', 'date_format', 'time_format')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'password_changed_at', 
                      'last_active')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 
                      'user_permissions'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tenant'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined', 'password_changed_at', 
                      'last_active', 'api_key')
    
    actions = ['activate_users', 'deactivate_users', 'force_password_reset']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = _("Activate selected users")

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = _("Deactivate selected users")

    def force_password_reset(self, request, queryset):
        queryset.update(force_password_change=True)
    force_password_reset.short_description = _("Force password reset for selected users")

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'description', 'created_at')
    list_filter = ('tenant', 'created_at')
    search_fields = ('name', 'description', 'tenant__name')
    
    fieldsets = (
        (None, {
            'fields': ('tenant', 'name', 'description')
        }),
        (_('Module Permissions'), {
            'fields': (
                'can_manage_users',
                'can_manage_roles',
                'can_manage_clients',
                'can_manage_projects',
                'can_manage_invoices',
                'can_manage_expenses',
                'can_manage_settings',
            )
        }),
        (_('Custom Permissions'), {
            'fields': ('custom_permissions',),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at', 'expires_at', 
                   'is_active')
    list_filter = ('is_active', 'assigned_at', 'expires_at')
    search_fields = ('user__email', 'role__name', 'assigned_by__email')
    raw_id_fields = ('user', 'role', 'assigned_by')
    
    actions = ['activate_roles', 'deactivate_roles']

    def activate_roles(self, request, queryset):
        queryset.update(is_active=True)
    activate_roles.short_description = _("Activate selected role assignments")

    def deactivate_roles(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_roles.short_description = _("Deactivate selected role assignments")

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'created_at', 'successful', 
                   'failure_reason')
    list_filter = ('successful', 'created_at')
    search_fields = ('email', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'email', 'ip_address', 'user_agent', 'successful', 
                      'failure_reason', 'created_at')
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Only allow deleting records older than 90 days
        if obj:
            return (timezone.now() - obj.created_at).days > 90
        return True
