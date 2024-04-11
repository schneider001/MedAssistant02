from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Doctor.objects.create(user=instance)
    
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.doctor.save()


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

    @classmethod
    def find_all(cls, per_page):
        return cls.objects.order_by('name')[:per_page]

    @classmethod
    def find_by_name_and_certificate(cls, search, per_page):
        return cls.objects.filter(
            models.Q(name__icontains=search) |
            models.Q(insurance_certificate__icontains=search)
        ).order_by('-name')[:per_page]

    @classmethod
    def get_name_by_request_id(cls, request_id):
        return cls.objects.filter(patient__request__id=request_id).values_list('name', flat=True).first()


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

    @classmethod
    def get_requests_page_by_patient_id(cls, patient_id, per_page):
        return Request.objects.filter(patient_id=patient_id).annotate(
            doctor_name=F('doctor__name'),
            disease_ru_name=F('predicted_disease__ru_name')
        ).values('id', 'doctor_name', 'date', 'disease_ru_name', 'is_commented')[:per_page]
    
    @classmethod
    def get_requests_page_by_doctor_id_contain_substr(cls, doctor_id, search, per_page):
        return cls.objects.filter(
            doctor_id=doctor_id
        ).annotate(
            disease_name=F('predicted_disease__ru_name'),
            patient_name=F('patient__name'),
        ).filter(
            models.Q(disease_name__icontains=search) | models.Q(patient_name__icontains=search)
        ).values(
            'id', 'patient_name', 'date', 'disease_name', 'is_commented'
        ).order_by(
            '-disease_name', 'patient_name', '-date'
        )[:per_page]
    
    @classmethod
    def get_requests_page_by_doctor_id(cls, doctor_id, per_page):
        return cls.objects.filter(
            doctor_id=doctor_id
        ).annotate(
            patient_name=F('patient__name'),
            disease_name=F('predicted_disease__ru_name')
        ).values(
            'id', 'patient_name', 'date', 'disease_name', 'is_commented'
        ).order_by(
            '-date', 'patient_name'
        )[:per_page]
    
    @classmethod
    def add(cls, doctor_id, patient_id, symptom_ids, ml_model_version):
        ml_model = MLModel.objects.get(version=ml_model_version)
        request = cls.objects.create(doctor_id=doctor_id, patient_id=patient_id, ml_model=ml_model)

        for symptom_id in symptom_ids:
            symptom = Symptom.objects.get(id=symptom_id)
            RequestSymptom.objects.create(request=request, symptom=symptom)

        return request.id

    def update_status(self, status, predicted_disease_id):
        self.status = status
        self.predicted_disease_id = predicted_disease_id
        self.save()
    
    def get_symptom_ru_names(request_id):
        symptoms = Symptom.objects.filter(requestsymptom__request_id=request_id)
        return list(symptoms.values_list('ru_name', flat=True))
    

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

    def get_comments_by_request_id(request_id, doctor_id):
        comments = Comment.objects.filter(
            request_id=request_id,
            status=Comment.NEW
        ).select_related('doctor').order_by('-id')

        comments_list = []
        for comment in comments:
            is_own_comment = 1 if comment.doctor_id == doctor_id else 0
            comments_list.append({
                'comments_id': comment.id,
                'name': comment.doctor.name,
                'date': comment.date,
                'comment': comment.comment,
                'is_own_comment': is_own_comment
            })

        return comments_list


@receiver(post_save, sender=Comment)
def update_request_is_commented(sender, instance, created, **kwargs):
    if created:
        Request.objects.filter(id=instance.request_id).update(is_commented=True)

@receiver(post_delete, sender=Comment)
def update_request_is_commented_on_delete(sender, instance, **kwargs):
    Request.objects.filter(id=instance.request_id).update(is_commented=Comment.objects.filter(request_id=instance.request_id, status=Comment.NEW).exists())