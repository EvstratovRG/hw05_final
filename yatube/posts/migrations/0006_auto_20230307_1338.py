# Generated by Django 2.2.6 on 2023-03-07 10:38

from django.db import migrations, models
import posts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20230307_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(validators=[posts.validators.validate_not_empty]),
        ),
    ]