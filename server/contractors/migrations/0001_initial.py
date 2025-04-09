# Generated by Django 5.0.7 on 2025-04-06 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorPortfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='contractor_portfolio/')),
                ('completion_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContractorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_name', models.CharField(max_length=255)),
                ('business_description', models.TextField(blank=True)),
                ('years_of_experience', models.PositiveIntegerField(default=0)),
                ('license_number', models.CharField(blank=True, max_length=100)),
                ('insurance_info', models.CharField(blank=True, max_length=255)),
                ('service_radius', models.PositiveIntegerField(default=50, help_text='Service radius in miles')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='contractor_profiles/')),
                ('is_onboarded', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContractorReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])),
                ('comment', models.TextField()),
                ('is_verified', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Service Categories',
            },
        ),
    ]
