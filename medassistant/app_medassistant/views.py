from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Patient, Request


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
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, полис ОМС; также переменную more, указывающая о конце пагинации.
    """
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


@login_required
def load_data_requests(request):
    """
    Получает список запросов для текущего пользователя для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, включая id запроса, имя пациента, дату, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    search = request.GET.get('search', '').lower()

    per_page = 100

    if len(search) > 3:
        requests = Request.get_requests_page_by_doctor_id_contain_substr(request.user.id, search, per_page)
    else:
        requests = Request.get_requests_page_by_doctor_id(request.user.id, per_page)

    request_data = [{
        'id': request['id'],
        'name': request['patient_name'],
        'date': request['date'].strftime("%Y-%m-%d %H:%M:%S"),
        'diagnosis': request['disease_name'],
        'is_commented': request['is_commented']
    } for request in requests]

    return JsonResponse({'results': request_data, 'pagination': {'more': False}}) #Убрать more

"""
@login_required
def load_patient_history(request):

    patient_id = request.GET.get('search', '')
    if not patient_id:
        return JsonResponse({}, status=400)

    try:
        patient_id = int(patient_id)
    except ValueError:
        return JsonResponse({}, status=400)

    per_page = 100

    requests = Request.get_requests_page_by_patient_id(patient_id, per_page)

    request_data = [{
        'id': request.id,
        'name': request.doctor.name,
        'date': request.date.strftime("%Y-%m-%d %H:%M:%S"),
        'diagnosis': request.predicted_disease.ru_name if request.predicted_disease else None,
        'is_commented': 'Прокомментирован' if request.is_commented else 'Без комментариев'
    } for request in requests]

    return JsonResponse({'results': request_data, 'pagination': {'more': False}}) #Убрать more
"""