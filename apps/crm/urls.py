from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Client URLs
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<uuid:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<uuid:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<uuid:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Contact URLs
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/add/', views.ContactCreateView.as_view(), name='contact_add'),
    path('contacts/<uuid:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<uuid:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_edit'),
    path('contacts/<uuid:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),

    # Lead URLs
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/add/', views.LeadCreateView.as_view(), name='lead_add'),
    path('leads/<uuid:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<uuid:pk>/edit/', views.LeadUpdateView.as_view(), name='lead_edit'),
    path('leads/<uuid:pk>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    path('leads/<uuid:pk>/update-status/', views.LeadStatusUpdateView.as_view(), name='lead_update_status'),
    path('leads/google-webhook/', views.GoogleLeadWebhookView.as_view(), name='google_lead_webhook'),
    path('leads/meta-webhook/', views.MetaLeadWebhookView.as_view(), name='meta_lead_webhook'),

    # Communication URLs
    path('communications/', views.CommunicationListView.as_view(), name='communication_list'),
    path('communications/add/', views.CommunicationCreateView.as_view(), name='communication_add'),
    path('communications/<uuid:pk>/', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('communications/<uuid:pk>/edit/', views.CommunicationUpdateView.as_view(), name='communication_edit'),
    path('communications/<uuid:pk>/delete/', views.CommunicationDeleteView.as_view(), name='communication_delete'),

    # Document URLs
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/add/', views.DocumentCreateView.as_view(), name='document_add'),
    path('documents/<uuid:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<uuid:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_edit'),
    path('documents/<uuid:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
]
