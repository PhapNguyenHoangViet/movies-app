# Generated by Django 4.0.10 on 2024-11-08 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_user_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sex',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
