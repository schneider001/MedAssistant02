import django
from csv import reader
from datetime import datetime, timedelta
from random import randint, choice, sample
import string
import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
sys.path.append(parent_directory)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medassistant.settings')

django.setup()

from app_medassistant.models import Doctor, Patient, Request, Symptom, Disease, Comment, RequestSymptom, MLModel
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes

def fill_from_dataset(filepath, model_class):
    with open(filepath, 'r', encoding='utf-8') as csv_file:
        _reader = reader(csv_file)
        for row in _reader:
            model_class.objects.get_or_create(name=row[0], ru_name=row[2])

def get_random_timestamp():
    return datetime.now() - timedelta(weeks=randint(0, 2000))

def get_random_snils():
    return f"{randint(100, 999)}-{randint(10, 99)}-{randint(100, 999)} {randint(10, 99)}"

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for i in range(length))

def populate_database():
    # Заполнение таблиц симптомов и заболеваний
    fill_from_dataset("../../datasets/Symptom-severity_ru.csv", Symptom)
    fill_from_dataset("../../datasets/symptom_Description_ru.csv", Disease)

    # Создание пациентов
    first_names = ["Иван", "Петр", "Сидор", "Алексей", "Дмитрий", "Николай", "Василий", "Андрей", "Сергей", "Михаил"]
    surnames = ["Иванов", "Петров", "Сидоров", "Алексеев", "Дмитриев", "Николаев", "Васильев", "Андреев", "Сергеев", "Михайлов"]
    for i in range(100):
        name = f"{choice(surnames)} {choice(first_names)} {choice(first_names)}ович"
        snils = get_random_snils()
        born_date = get_random_timestamp()
        sex = 'MALE'
        Patient.objects.create(name=name, insurance_certificate=snils, born_date=born_date, sex=sex)

    # Создание докторов
    doctors = [
        ("doctor1", "Николаев Николай Николаевич", '1'), 
        ("doctor2", "Васильев Василий Васильевич", '2'), 
        ("doctor3", "Андреев Андрей Андреевич", '3'),
        ("doctor4", "Сергеев Сергей Сергеевич", '4'),
        ("doctor5", "Михайлов Михаил Михайлович", '5')
    ]
    for username, name, password in doctors:
        user = User.objects.create(username=username)
        user.set_password(password)
        user.doctor.name = name
        user.save()

    # Создание запросов
    for i in range(200):
        doctor_id = randint(1, len(doctors))
        patient_id = randint(1, 100)  
        predicted_disease_id = randint(1, 40)
        status = 'READY'
        date = get_random_timestamp()
        is_commented = False
        request = Request.objects.create(doctor_id=doctor_id, patient_id=patient_id, status=status, date=date, predicted_disease_id=predicted_disease_id, is_commented=is_commented)

        # Создание симптомов для запроса
        used_symptoms = set()
        for j in range(randint(1, 6)):
            symptom_id = randint(1, 130)
            while symptom_id in used_symptoms:
                symptom_id = randint(1, 130)
            used_symptoms.add(symptom_id)
            RequestSymptom.objects.create(symptom_id=symptom_id, request_id=request.id)

        # Создание комментариев для запроса
        rand_arr = sample(range(1, len(doctors) + 1), 3)
        for k in range(randint(0, 3)):
            timestamp = get_random_timestamp()
            status = 'NEW'
            Comment.objects.create(doctor_id=rand_arr[k], request_id=request.id, comment=get_random_string(25), date=timestamp, status=status)

    # Создание записи о модели
    MLModel.objects.create(hash=force_bytes('some_hash'), version="1.0") #Вынести версию модели в конфиг

# Заполнение базы данных
populate_database()
