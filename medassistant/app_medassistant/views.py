from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Patient


def login_view(request):
    """
    Отображает страницу входа и обрабатывает вход пользователя.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.doctor is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    else:
        return render(request, 'login.html')


@login_required
def logout_view(request):
    """
    Обрабатывает выход пользователя.
    """
    logout(request)
    return redirect('login')


@login_required
def main(request):
    """
    Отображает главную страницу.
    """
    show_sidebar = True
    return render(request, 'index.html', {'show_sidebar': show_sidebar})


@login_required
def patients(request):
    """
    Отображает страницу с пациентами.
    """
    show_sidebar = True
    return render(request, 'patients.html', {'show_sidebar': show_sidebar})


@login_required
def load_patients(request):
    search = request.GET.get('search', '')
    per_page = 100

    if len(search) > 3:
        patients = Patient.find_by_name_and_certificate(search, per_page)
    else:
        patients = Patient.find_all(per_page)

    patients_data = [{'id': patient.id, 'name': patient.name, 'oms': patient.insurance_certificate} for patient in patients]
    return JsonResponse({'results': patients_data, 'pagination': {'more': False}}) #Убрать more


@login_required
def history(request):
    """
    Отображает страницу с историей запросов.
    """
    show_sidebar = True
    return render(request, 'history.html', {'show_sidebar': show_sidebar})

