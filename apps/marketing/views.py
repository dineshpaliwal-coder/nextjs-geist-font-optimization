from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as AuthLoginView
from django.shortcuts import redirect
from .models import BlogPost, Testimonial, JobListing, FAQ, KnowledgebaseArticle
from .forms import ContactForm, SignupForm

class HomepageView(TemplateView):
    template_name = 'marketing/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.all()[:5]
        context['features'] = [
            'Client & Contact Management',
            'Lead Management',
            'Project Management',
            'Invoice & Estimate System',
            'Proposal & Contract Management',
            'Task & Calendar',
            'Support Tickets',
            'Knowledgebase',
            'Time & Expense Tracking',
            'Reports & Dashboards',
            'Human Resources Module',
            'Affiliate/Partner Program',
        ]
        return context

class FeaturesView(TemplateView):
    template_name = 'marketing/features.html'

class PricingView(TemplateView):
    template_name = 'marketing/pricing.html'

class AboutView(TemplateView):
    template_name = 'marketing/about.html'

class ContactView(FormView):
    template_name = 'marketing/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('marketing:contact')

    def form_valid(self, form):
        # Process contact form submission (e.g., send email)
        # For now, just redirect with success message
        return super().form_valid(form)

class BlogListView(ListView):
    model = BlogPost
    template_name = 'marketing/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by('-published_at')

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'marketing/blog_detail.html'
    context_object_name = 'post'

class CareersListView(ListView):
    model = JobListing
    template_name = 'marketing/careers_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        return JobListing.objects.filter(is_open=True).order_by('-posted_at')

class CareerDetailView(DetailView):
    model = JobListing
    template_name = 'marketing/career_detail.html'
    context_object_name = 'job'

class TermsView(TemplateView):
    template_name = 'marketing/legal/terms.html'

class PrivacyView(TemplateView):
    template_name = 'marketing/legal/privacy.html'

class CookiesView(TemplateView):
    template_name = 'marketing/legal/cookies.html'

class KnowledgebaseListView(ListView):
    model = KnowledgebaseArticle
    template_name = 'marketing/knowledgebase_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return KnowledgebaseArticle.objects.filter(is_published=True).order_by('-published_at')

class KnowledgebaseDetailView(DetailView):
    model = KnowledgebaseArticle
    template_name = 'marketing/knowledgebase_detail.html'
    context_object_name = 'article'

class LoginView(AuthLoginView):
    template_name = 'marketing/login.html'

class SignupView(FormView):
    template_name = 'marketing/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('marketing:login')

    def form_valid(self, form):
        # Process signup logic here
        return super().form_valid(form)
