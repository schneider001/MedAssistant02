from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login', views.login_view, name='login_post'),
    path('logout', views.logout_view, name='logout'),
    path('main', views.main, name='main'),
    path('patients', views.patients, name='patients'),
    path('load_patients', views.load_patients, name='load_patients'),
    path('history', views.history, name='history'),
    path('load_data_requests', views.load_data_requests, name='load_data_requests'),
    path('get_patient_info', views.get_patient_info, name='get_patient_info'),
    path('load_patient_history', views.load_patient_history, name='load_patient_history'),
    path('create_patient', views.create_patient, name='create_patient'),
    path('load_symptoms', views.load_symptoms, name='load_symptoms'),
]