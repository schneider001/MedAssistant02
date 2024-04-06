from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password


class Doctor(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    USERNAME_FIELD = 'username'


class Patient(models.Model):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    ANOTHER = 'ANOTHER'
    SEX_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (ANOTHER, 'Another'),
    ]

    name = models.CharField(max_length=255)
    insurance_certificate = models.CharField(max_length=255, unique=True)
    born_date = models.DateTimeField(null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)


class Administrator(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    USERNAME_FIELD = 'username'


class Symptom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ru_name = models.CharField(max_length=255, unique=True)


class Disease(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ru_name = models.CharField(max_length=255, unique=True)


class MLModel(models.Model):
    hash = models.BinaryField()
    version = models.CharField(max_length=255)


class Request(models.Model):
    IN_PROGRESS = 'IN_PROGRESS'
    READY = 'READY'
    ERROR = 'ERROR'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'In Progress'),
        (READY, 'Ready'),
        (ERROR, 'Error'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    date = models.DateTimeField(auto_now_add=True)
    is_commented = models.BooleanField(default=False)

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    predicted_disease = models.ForeignKey(Disease, null=True, on_delete=models.CASCADE)
    ml_model = models.ForeignKey(MLModel, null=True, on_delete=models.CASCADE)


class RequestSymptom(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)


class Comment(models.Model):
    OLD = 'OLD'
    NEW = 'NEW'
    STATUS_CHOICES = [
        (OLD, 'Old'),
        (NEW, 'New'),
    ]

    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=NEW)

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

