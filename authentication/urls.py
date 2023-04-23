from django.urls import path
from django.views.generic import TemplateView
from .views import LoginView, RegisterView, IndexView

app_name = 'authentication'

urlpatterns = [
    path('', IndexView.as_view(template_name='authentication/index.html'), name='index'),
    path('login/', LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('register/', RegisterView.as_view(template_name='authentication/register.html'), name='register'),
]
