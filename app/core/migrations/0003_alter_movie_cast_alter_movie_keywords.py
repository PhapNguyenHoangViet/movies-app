# Generated by Django 4.0.10 on 2024-11-13 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_movie_imdb_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='cast',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='keywords',
            field=models.JSONField(blank=True, null=True),
        ),
    ]