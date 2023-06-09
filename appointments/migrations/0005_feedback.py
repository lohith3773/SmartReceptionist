# Generated by Django 4.2.1 on 2023-06-18 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('subject', models.CharField(choices=[('APPOINTMENT', 'Appointment'), ('FEEDBACK', 'Feedback'), ('NEW_FEATURE', 'Feature Request'), ('BUG', 'Bug'), ('OTHER', 'Other')], default='Appointment', max_length=50)),
                ('message', models.CharField(max_length=255)),
            ],
        ),
    ]
