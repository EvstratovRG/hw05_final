# Generated by Django 2.2.16 on 2023-03-27 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_follow'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
