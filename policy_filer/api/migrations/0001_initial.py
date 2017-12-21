# Generated by Django 2.0 on 2017-12-19 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=3)),
                ('policy_number', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('PE', 'Pending'), ('PR', 'Processed'), ('AK', 'Acknowledged')], default='P', max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
