from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='home'),  # Redirige la racine vers la page de login ou dashboard
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('deposit/', deposit_view, name='deposit'),
    path('withdraw/', withdraw_view, name='withdraw'),
]
