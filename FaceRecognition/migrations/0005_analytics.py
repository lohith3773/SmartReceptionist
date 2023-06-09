# Generated by Django 4.2.1 on 2023-06-23 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FaceRecognition', '0004_manager_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_time', models.DateTimeField(auto_now_add=True)),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VisitorAnalytics', to='FaceRecognition.visitor')),
            ],
        ),
    ]
