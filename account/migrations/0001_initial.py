# Generated by Django 4.2.6 on 2023-12-14 16:32

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("email", models.EmailField(max_length=100, unique=True)),
                ("username", models.CharField(max_length=100, unique=True)),
                ("join_date", models.DateTimeField(auto_now_add=True)),
                ("last_login", models.DateTimeField(auto_now=True)),
                ("is_admin", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_superuser", models.BooleanField(default=False)),
                (
                    "profile_image",
                    models.ImageField(
                        blank=True,
                        default="images/default_profile.png",
                        max_length=255,
                        null=True,
                        upload_to=account.models.get_profile_image_path,
                    ),
                ),
                ("hide_email", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
