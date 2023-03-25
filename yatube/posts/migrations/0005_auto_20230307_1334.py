# Generated by Django 2.2.6 on 2023-03-07 10:34

from django.db import migrations, models
import posts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20230303_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(blank=True, default='', validators=[posts.validators.validate_not_empty]),
        ),
    ]
