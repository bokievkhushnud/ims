# Generated by Django 4.1.3 on 2023-02-17 19:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("www", "0002_alter_item_holder"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="item",
            name="holder",
        ),
        migrations.AddField(
            model_name="item",
            name="holder",
            field=models.ManyToManyField(
                blank=True, related_name="holder", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
