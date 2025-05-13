from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import Client, Contact, Lead, Communication, Document

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'crm/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(tenant=self.request.tenant, is_active=True)

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'crm/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        return Client.objects.filter(tenant=self.request.tenant)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['name', 'website', 'email', 'phone', 'address', 'tags', 'is_active']
    template_name = 'crm/client_form.html'
    success_url = reverse_lazy('crm:client_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['name', 'website', 'email', 'phone', 'address', 'tags', 'is_active']
    template_name = 'crm/client_form.html'
    success_url = reverse_lazy('crm:client_list')

    def get_queryset(self):
        return Client.objects.filter(tenant=self.request.tenant)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'crm/client_confirm_delete.html'
    success_url = reverse_lazy('crm:client_list')

    def get_queryset(self):
        return Client.objects.filter(tenant=self.request.tenant)

# Similar views for Contact

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'crm/contact_list.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.filter(tenant=self.request.tenant, is_active=True)

class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'crm/contact_detail.html'
    context_object_name = 'contact'

    def get_queryset(self):
        return Contact.objects.filter(tenant=self.request.tenant)

class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    fields = ['client', 'first_name', 'last_name', 'email', 'phone', 'job_title', 'tags', 'is_primary', 'is_active']
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contact_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)

class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    fields = ['client', 'first_name', 'last_name', 'email', 'phone', 'job_title', 'tags', 'is_primary', 'is_active']
    template_name = 'crm/contact_form.html'
    success_url = reverse_lazy('crm:contact_list')

    def get_queryset(self):
        return Contact.objects.filter(tenant=self.request.tenant)

class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'crm/contact_confirm_delete.html'
    success_url = reverse_lazy('crm:contact_list')

    def get_queryset(self):
        return Contact.objects.filter(tenant=self.request.tenant)

# Similar views for Lead

class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'crm/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        return Lead.objects.filter(tenant=self.request.tenant, is_active=True)

class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'crm/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        return Lead.objects.filter(tenant=self.request.tenant)

class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    fields = ['client', 'first_name', 'last_name', 'email', 'phone', 'source', 'status', 'score', 'notes', 'is_active']
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)

class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    fields = ['client', 'first_name', 'last_name', 'email', 'phone', 'source', 'status', 'score', 'notes', 'is_active']
    template_name = 'crm/lead_form.html'
    success_url = reverse_lazy('crm:lead_list')

    def get_queryset(self):
        return Lead.objects.filter(tenant=self.request.tenant)

class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = 'crm/lead_confirm_delete.html'
    success_url = reverse_lazy('crm:lead_list')

    def get_queryset(self):
        return Lead.objects.filter(tenant=self.request.tenant)

# Similar views for Communication

class CommunicationListView(LoginRequiredMixin, ListView):
    model = Communication
    template_name = 'crm/communication_list.html'
    context_object_name = 'communications'

    def get_queryset(self):
        return Communication.objects.filter(tenant=self.request.tenant)

class CommunicationDetailView(LoginRequiredMixin, DetailView):
    model = Communication
    template_name = 'crm/communication_detail.html'
    context_object_name = 'communication'

    def get_queryset(self):
        return Communication.objects.filter(tenant=self.request.tenant)

class CommunicationCreateView(LoginRequiredMixin, CreateView):
    model = Communication
    fields = ['client', 'contact', 'communication_type', 'subject', 'body', 'date']
    template_name = 'crm/communication_form.html'
    success_url = reverse_lazy('crm:communication_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CommunicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Communication
    fields = ['client', 'contact', 'communication_type', 'subject', 'body', 'date']
    template_name = 'crm/communication_form.html'
    success_url = reverse_lazy('crm:communication_list')

    def get_queryset(self):
        return Communication.objects.filter(tenant=self.request.tenant)

class CommunicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Communication
    template_name = 'crm/communication_confirm_delete.html'
    success_url = reverse_lazy('crm:communication_list')

    def get_queryset(self):
        return Communication.objects.filter(tenant=self.request.tenant)

# Similar views for Document

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'crm/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return Document.objects.filter(tenant=self.request.tenant)

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'crm/document_detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        return Document.objects.filter(tenant=self.request.tenant)

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    fields = ['client', 'lead', 'file', 'description']
    template_name = 'crm/document_form.html'
    success_url = reverse_lazy('crm:document_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    fields = ['client', 'lead', 'file', 'description']
    template_name = 'crm/document_form.html'
    success_url = reverse_lazy('crm:document_list')

    def get_queryset(self):
        return Document.objects.filter(tenant=self.request.tenant)

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'crm/document_confirm_delete.html'
    success_url = reverse_lazy('crm:document_list')

    def get_queryset(self):
        return Document.objects.filter(tenant=self.request.tenant)

# API view to update lead status
@method_decorator(csrf_exempt, name='dispatch')
class LeadStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    fields = ['status']
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            status = data.get('status')
            if status not in dict(Lead.LEAD_STATUS_CHOICES):
                return HttpResponseBadRequest('Invalid status value')
            lead = self.get_object()
            lead.status = status
            lead.save()
            return JsonResponse({'message': 'Lead status updated successfully'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

# Webhook endpoint to receive Google leads
@method_decorator(csrf_exempt, name='dispatch')
class GoogleLeadWebhookView(LoginRequiredMixin, CreateView):
    model = Lead
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            # Extract lead info from Google webhook payload
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            source = 'Google'
            lead = Lead.objects.create(
                tenant=request.tenant,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                source=source,
                status='new',
                is_active=True
            )
            return JsonResponse({'message': 'Google lead imported successfully'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

# Webhook endpoint to receive Meta leads
@method_decorator(csrf_exempt, name='dispatch')
class MetaLeadWebhookView(LoginRequiredMixin, CreateView):
    model = Lead
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            # Extract lead info from Meta webhook payload
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            source = 'Meta'
            lead = Lead.objects.create(
                tenant=request.tenant,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                source=source,
                status='new',
                is_active=True
            )
            return JsonResponse({'message': 'Meta lead imported successfully'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
