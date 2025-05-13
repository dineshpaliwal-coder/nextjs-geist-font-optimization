from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.HomepageView.as_view(), name='homepage'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('careers/', views.CareersListView.as_view(), name='careers_list'),
    path('careers/<uuid:pk>/', views.CareerDetailView.as_view(), name='career_detail'),
    path('legal/terms/', views.TermsView.as_view(), name='terms'),
    path('legal/privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('legal/cookies/', views.CookiesView.as_view(), name='cookies'),
    path('knowledgebase/', views.KnowledgebaseListView.as_view(), name='knowledgebase_list'),
    path('knowledgebase/<slug:slug>/', views.KnowledgebaseDetailView.as_view(), name='knowledgebase_detail'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
]
