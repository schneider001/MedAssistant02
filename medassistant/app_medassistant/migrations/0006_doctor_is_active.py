# Generated by Django 5.0.3 on 2024-04-06 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_medassistant', '0005_delete_administrator'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]