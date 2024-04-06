from csv import reader
from datetime import datetime, timedelta
from random import randint, choice, sample
import string
import json
from passlib.hash import bcrypt
import psycopg2


with open('../configs/db_settings.json', 'r') as options_file:
	conn_data=json.load(options_file)

conn = psycopg2.connect(
    dbname=conn_data['database'],
    user=conn_data['user'],
    password=conn_data['password'],
    host=conn_data['host']
)
cur = conn.cursor()


def fill_from_dataset(filepath, tablename):
    data_set = set()
    with open(filepath, 'r', encoding='utf-8') as csv_file:
        _reader = reader(csv_file)
        header = next(_reader)
        for row in _reader:
            if row[0] not in data_set:
                data_set.add(row[0])
                query = f"INSERT INTO {tablename} (name, ru_name) VALUES (%s, %s)"
                cur.execute(query, (row[0], row[2]))

def fill_sympt_diseases():
    fill_from_dataset("../datasets/Symptom-severity_ru.csv", "app_medassistant_symptom")
    fill_from_dataset("../datasets/symptom_Description_ru.csv", "app_medassistant_disease")
    conn.commit()


def get_random_timestamp():
    return datetime.now() - timedelta(weeks=randint(0, 2000))

def get_random_snils():
    return f"{randint(100, 999)}-{randint(10, 99)}-{randint(100, 999)} {randint(10, 99)}"

def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for i in range(length))

def populate_database():
    first_names = ["Иван", "Петр", "Сидор", "Алексей", "Дмитрий", "Николай", "Василий", "Андрей", "Сергей", "Михаил"]
    surnames = ["Иванов", "Петров", "Сидоров", "Алексеев", "Дмитриев", "Николаев", "Васильев", "Андреев", "Сергеев", "Михайлов"]

    doctors = [
        ("doctor1", "Николаев Николай Николаевич", bcrypt.hash('1'), get_random_timestamp()), 
        ("doctor2", "Васильев Василий Васильевич", bcrypt.hash('2'), get_random_timestamp()), 
        ("doctor3", "Андреев Андрей Андреевич", bcrypt.hash('3'), get_random_timestamp()),
        ("doctor4", "Сергеев Сергей Сергеевич", bcrypt.hash('4'), get_random_timestamp()),
        ("doctor5", "Михайлов Михаил Михайлович", bcrypt.hash('5'), get_random_timestamp())
    ]
    admins = [
        ("admin1", "Владимиров Владимир Владимирович", bcrypt.hash('123')),
        ("admin2", "Егоров Erop Егорович", bcrypt.hash('321'))
    ]
    
    for i in range(100):  
        name = f"{choice(surnames)} {choice(first_names)} {choice(first_names)}ович"
        snils = get_random_snils()
        timestamp = get_random_timestamp()
        sex = 'MALE'
        query = "INSERT INTO app_medassistant_patient (name, insurance_certificate, born_date, sex) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (name, snils, timestamp, sex))
        
    for person in doctors:
        query = "INSERT INTO app_medassistant_doctor (username, name, password_hash, last_login) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (*person,))
        
    for person in admins:
        query = "INSERT INTO app_medassistant_administrator (username, name, password_hash) VALUES (%s, %s, %s)"
        cur.execute(query, (*person,))
        
    for x in range(200):  
        doctor_id = randint(1, len(doctors))
        patient_id = randint(1, 100)  
        predicted_disease_id = randint(1, 40)
        status = 'READY'
        timestamp = get_random_timestamp()
        is_commented = False
        query = "INSERT INTO app_medassistant_request (doctor_id, patient_id, status, date, predicted_disease_id, is_commented) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(query, (doctor_id, patient_id, status, timestamp, predicted_disease_id, is_commented))
        
        used_symptoms = set()
        for symt_num in range(randint(1, 6)):
            symptom_id = randint(1, 130)
            while symptom_id in used_symptoms:
                symptom_id = randint(1, 130)
            used_symptoms.add(symptom_id)
            query = "INSERT INTO app_medassistant_requestsymptom (symptom_id, request_id) VALUES (%s, %s)"
            cur.execute(query, (symptom_id, x+1))
        
        rand_arr = sample(range(1, len(doctors) + 1), 3)
        for comm_num in range(randint(0, 3)):
            timestamp = get_random_timestamp()
            status = 'NEW'
            query = "INSERT INTO app_medassistant_comment (doctor_id, request_id, comment, date, status) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(query, (rand_arr[comm_num], x+1, get_random_string(25), timestamp, status))
    
    conn.commit()


fill_sympt_diseases()
populate_database()

cur.close()
conn.close()