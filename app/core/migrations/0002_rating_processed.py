# Generated by Django 4.0.10 on 2024-12-04 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]