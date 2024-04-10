from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import os
from datetime import datetime
from .models import Patient, Request, Symptom


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


@login_required
def load_patient_history(request):
    """
    Получает список запросов для пациента по id пациента для указанной странице в пагинации.
    :param str patient_id: ID пациента.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, которые включают id запроса, имя доктора, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
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
        'id': request['id'],
        'name': request['doctor_name'],
        'date': request['date'].strftime("%Y-%m-%d %H:%M:%S"),
        'diagnosis': request['disease_ru_name'],
        'is_commented': request['is_commented']
    } for request in requests]

    return JsonResponse({'results': request_data, 'pagination': {'more': False}}) #Убрать more


@login_required
def get_patient_info(request):
    """
    Получает информацию о пациенте по его id.
    :param str patient_id: ID пациента.
    :return: JSON-ответ с информацией о пациенте, включая его id, полное имя, дату рождения, текущий возраст, Полис ОМС, пол.
    """
    patient_id = request.GET.get('patient_id')

    patient = get_object_or_404(Patient, id=patient_id)

    today = datetime.now()
    age = today.year - patient.born_date.year - \
        ((today.month, today.day) < (patient.born_date.month, patient.born_date.day))

    patient_data = {
        'id': patient.id,
        'name': patient.name,
        'birthDate': patient.born_date.strftime("%Y-%m-%d"),
        'age': age,
        'oms': patient.insurance_certificate,
        'sex': patient.sex,
    }

    photo_filename = f'static/patient_images/{patient_id}.jpg'
    if os.path.exists(photo_filename):
        patient_data['photo_url'] = photo_filename

    return JsonResponse(patient_data)


@login_required
def load_symptoms(request):
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком симптомов для указанной страницы, включая id симптома, название, также переменную more, указывающая о конце пагинации.
    """
    search = request.GET.get('search', '').lower()
    page = int(request.GET.get('page', 1))

    per_page = 10

    symptoms = Symptom.objects.all()
    
    if search != '':
        symptoms = [row for row in symptoms if search in row.ru_name]
    
    start = (page - 1) * per_page
    end = start + per_page
    symptoms = symptoms[start:end]

    request_data = [{
        'id': symptom.id,
        'name': symptom.ru_name,
    } for symptom in symptoms]

    return JsonResponse({'results': request_data, 'pagination': {'more': len(request_data) == per_page}})

