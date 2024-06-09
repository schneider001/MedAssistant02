import os
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.templatetags.static import static
from datetime import datetime
from urllib.parse import urlparse
from .models import Patient, Request, Symptom, Disease, Comment
from . import get_disease, ML_MODEL_VERSION
import logging

logger = logging.getLogger('django')

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
            logger.info(f"User {username} logged in successfully.")
            return JsonResponse({'success': True})
        else:
            logger.warning(f"Failed login attempt for {username}.")
            return JsonResponse({'success': False})
    else:
        return render(request, 'login.html')


@login_required
def logout_view(request):
    """
    Обрабатывает выход пользователя.
    """
    username = request.user.username
    logout(request)
    logger.info(f"User {username} logged out.")
    return redirect('login')


@login_required
def main(request):
    """
    Отображает главную страницу.
    """
    logger.info("Accessed the main page.")
    return render(request, 'index.html', {'show_sidebar': True})


@login_required
def patients(request):
    """
    Отображает страницу с пациентами.
    """
    logger.info("Accessed the patients page.")
    return render(request, 'patients.html', {'show_sidebar': True})


@login_required
def load_patients(request):
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, полис ОМС; также переменную more, указывающая о конце пагинации.
    """
    search = request.GET.get('search', '')
    logger.debug(f"Searching for patients with filter: {search}")
    per_page = 100

    if len(search) > 3:
        patients = Patient.find_by_name_and_certificate(search, per_page)
    else:
        patients = Patient.find_all(per_page)

    patients_data = [{'id': patient.id, 'name': patient.name, 'oms': patient.insurance_certificate} for patient in patients]
    return JsonResponse({'results': patients_data, 'pagination': {'more': False}})


@login_required
def history(request):
    """
    Отображает страницу с историей запросов.
    """
    logger.info("Accessed the history page.")
    return render(request, 'history.html', {'show_sidebar': True})


@login_required
def load_data_requests(request):
    """
    Получает список запросов для текущего пользователя для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, включая id запроса, имя пациента, дату, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    search = request.GET.get('search', '').lower()
    logger.debug(f"Loading data requests with search filter: {search}")
    per_page = 100

    if len(search) > 3:
        requests = Request.get_requests_page_by_doctor_id_contain_substr(request.user.id, search, per_page)
    else:
        requests = Request.get_requests_page_by_doctor_id(request.user.id, per_page)

    request_data = [{
        'id': req['id'],
        'name': req['patient_name'],
        'date': req['date'].strftime("%Y-%m-%d %H:%M:%S"),
        'diagnosis': req['disease_name'],
        'is_commented': req['is_commented']
    } for req in requests]

    return JsonResponse({'results': request_data, 'pagination': {'more': False}})


@login_required
def load_patient_history(request):
    """
    Получает список запросов для пациента по id пациента для указанной странице в пагинации.
    :param str patient_id: ID пациента.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, которые включают id запроса, имя доктора, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    patient_id = request.GET.get('search', '')
    logger.debug(f"Loading history for patient ID: {patient_id}")
    if not patient_id:
        return JsonResponse({}, status=400)

    try:
        patient_id = int(patient_id)
    except ValueError:
        logger.error("Invalid patient ID format.")
        return JsonResponse({}, status=400)

    per_page = 100
    requests = Request.get_requests_page_by_patient_id(patient_id, per_page)

    request_data = [{
        'id': req['id'],
        'name': req['doctor_name'],
        'date': req['date'].strftime("%Y-%m-%d %H:%M:%S"),
        'diagnosis': req['disease_ru_name'],
        'is_commented': req['is_commented']
    } for req in requests]

    return JsonResponse({'results': request_data, 'pagination': {'more': False}})


@login_required
def get_patient_info(request):
    """
    Получает информацию о пациенте по его id.
    :param str patient_id: ID пациента.
    :return: JSON-ответ с информацией о пациенте, включая его id, полное имя, дату рождения, текущий возраст, Полис ОМС, пол.
    """
    patient_id = request.GET.get('patient_id')
    patient = get_object_or_404(Patient, id=patient_id)
    logger.info(f"Retrieved information for patient ID: {patient_id}")

    today = datetime.now()
    age = today.year - patient.born_date.year - ((today.month, today.day) < (patient.born_date.month, patient.born_date.day))

    patient_data = {
        'id': patient.id,
        'name': patient.name,
        'birthDate': patient.born_date.strftime("%Y-%m-%d"),
        'age': age,
        'oms': patient.insurance_certificate,
        'sex': patient.sex,
    }
    if settings.DEBUG:
        photo_filename = f'static/images/patient_images/{patient_id}.jpg' #Изменить путь для прода
        if os.path.exists(os.path.join('app_medassistant', photo_filename)):
            patient_data['photo_url'] = photo_filename
    else:
        photo_filename = f'{patient_id}.jpg'
        if default_storage.exists(photo_filename):
            url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, photo_filename))
            parts = urlparse(url)
            url_without_port = parts._replace(netloc=parts.hostname).geturl()
            patient_data['photo_url'] = url_without_port

    return JsonResponse(patient_data)


@login_required
def create_patient(request):
    """
    Создает нового пациента.
    :param str fullname: Имя пациента.
    :param str birthdate: Дата рождения.
    :param str oms: Полис ОМС пациента.
    :param image image: Изображение пациента.
    :return: JSON-ответ с информацией о пациенте, включая id пациента, имя пациента, Полис ОМС.
    """
    if request.method == 'POST':
        fullname = request.POST['fullname']
        birthdate = datetime.strptime(request.POST['birthdate'], '%d.%m.%Y')
        oms = request.POST['oms']
        sex = request.POST['sex']
        image = request.FILES.get('image')

        patient = Patient.objects.create(name=fullname, insurance_certificate=oms, born_date=birthdate, sex=sex)
        logger.info(f"Created new patient: {fullname}")

        if settings.DEBUG:
            directory_path = 'app_medassistant/static/images/patient_images/' #Изменить путь для прода
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            if image:
                with open(os.path.join(directory_path, f'{patient.id}.jpg'), 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
        else:
            if image:
                file_name = f'{patient.id}.jpg'
                file_name = default_storage.save(file_name, image)

        return JsonResponse({
            'id': patient.id,
            'name': patient.name,
            'oms': patient.insurance_certificate
        })


@login_required
def load_symptoms(request):
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком симптомов для указанной страницы, включая id симптома, название, также переменную more, указывающая о конце пагинации.
    """
    search = request.GET.get('search', '').lower()
    page = int(request.GET.get('page', 1))
    logger.debug(f"Loading symptoms for page {page} with filter: {search}")

    per_page = 10
    symptoms = Symptom.objects.all()
    if search:
        symptoms = [sym for sym in symptoms if search in sym.ru_name.lower()]

    start = (page - 1) * per_page
    end = start + per_page
    symptoms = symptoms[start:end]

    symptom_data = [{'id': sym.id, 'name': sym.ru_name} for sym in symptoms]

    return JsonResponse({'results': symptom_data, 'pagination': {'more': len(symptom_data) == per_page}})


@login_required
def get_request_info(request):
    """
    Получает диагноз с помощью модели и возвращает информацию об этом запросе.
    :param str id: ID пациента.
    :param str name: Полное имя пациента.
    :param str oms: Полис ОМС пациента.
    :param list symptoms: Список симптомов.
    :return: JSON-ответ с информацией для карточки запроса, включая id запроса, имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        patient_id = data.get('id')
        patient_name = data.get('name')
        symptom_ids = data.get('symptoms', [])

        try:
            symptoms = [Symptom.objects.get(id=id) for id in symptom_ids]
            logger.debug(f"Retrieved symptoms for patient {patient_name} with IDs: {symptom_ids}")
        except Exception as e:
            logger.error("Failed to retrieve symptoms", exc_info=True)
            return JsonResponse({'error': 'Symptom data retrieval failed'}, status=400)

        try:
            request_id = Request.add(request.user.id, patient_id, [symptom.id for symptom in symptoms], ML_MODEL_VERSION)
            disease_name = get_disease([symptom.name for symptom in symptoms])

            if disease_name:
                status = 'READY'
                disease = Disease.objects.get(name=disease_name)
            else:
                status = 'ERROR'
                disease = None

            request_instance = Request.objects.get(id=request_id)
            request_instance.update_status(status, disease.id if disease else None)
            logger.info(f"Request {request_id} processed with status {status} for disease {disease_name}")

            response_data = {
                'id': request_id,
                'patient_name': patient_name,
                'doctor': request.user.doctor.name,
                'symptoms': [symptom.ru_name for symptom in symptoms],
                'diagnosis': disease.ru_name if disease else "Not diagnosed",
                'doctor_comments': []
            }
            return JsonResponse(response_data)
        except Exception as e:
            logger.error("Failed to process medical request", exc_info=True)
            return JsonResponse({'error': 'Failed to process request'}, status=500)


@login_required
def get_request_info_by_id(request):
    """
    Получает возвращает информацию о запросе по его id из БД.
    :param str request_id: ID запроса.
    :return: JSON-ответ с информацией для карточки запроса, включая id запроса имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        request_id = data.get('request_id')

        try:
            request_details = Request.objects.get(id=request_id)
            symptoms = Request.get_symptom_ru_names(request_id)
            diagnosis_ru_name = request_details.predicted_disease.ru_name
            comments_values = Comment.get_comments_by_request_id(request_id, request.user.id)

            doctor_comments = [{
                'id': comment_values['comments_id'],
                'doctor': comment_values['name'],
                'time': comment_values['date'].strftime("%Y-%m-%d %H:%M:%S"),
                'comment': comment_values['comment'],
                'editable': comment_values['is_own_comment']
            } for comment_values in comments_values]

            response_data = {
                'id': request_id,
                'patient_name': request_details.patient.name,
                'doctor': request.user.doctor.name,
                'symptoms': symptoms,
                'diagnosis': diagnosis_ru_name,
                'doctor_comments': doctor_comments
            }
            logger.info(f"Retrieved request info for ID {request_id}")
            return JsonResponse(response_data)
        except Exception as e:
            logger.error(f"Failed to retrieve request info for ID {request_id}", exc_info=True)
            return JsonResponse({'error': 'Data retrieval failed'}, status=500)