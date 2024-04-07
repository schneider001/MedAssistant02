from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login', views.login_view, name='login_post'),
    path('logout', views.logout_view, name='logout'),
    path('main', views.main, name='main'),
    path('patients', views.patients, name='patients'),
    path('history', views.history, name='history'),
]