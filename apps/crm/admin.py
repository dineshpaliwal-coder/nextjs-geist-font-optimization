from django.contrib import admin
from .models import Client, Contact, Lead, Communication, Document

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'client', 'is_primary', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'client__name')
    list_filter = ('is_primary', 'is_active')
    ordering = ('last_name', 'first_name')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'score', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'source')
    list_filter = ('status', 'is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('communication_type', 'client', 'contact', 'subject', 'date', 'created_by')
    search_fields = ('subject', 'client__name', 'contact__first_name', 'contact__last_name')
    list_filter = ('communication_type', 'date')
    ordering = ('-date',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('client', 'lead', 'uploaded_by', 'file', 'created_at')
    search_fields = ('client__name', 'lead__first_name', 'lead__last_name', 'uploaded_by__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
