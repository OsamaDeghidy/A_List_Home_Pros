# Generated by Django 5.0.7 on 2025-04-06 22:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contractors', '0002_initial'),
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments_made', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payment',
            name='contractor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments_received', to='contractors.contractorprofile'),
        ),
        migrations.AddField(
            model_name='stripeaccount',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_account', to=settings.AUTH_USER_MODEL),
        ),
    ]
