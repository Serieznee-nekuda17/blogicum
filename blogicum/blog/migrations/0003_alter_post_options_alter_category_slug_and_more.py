# Generated by Django 5.1.1 on 2025-03-27 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_alter_category_options_alter_location_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={
                "ordering": ["-pub_date"],
                "verbose_name": "публикация",
                "verbose_name_plural": "Публикации",
            },
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(
                help_text="Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.",
                unique=True,
                verbose_name="Идентификатор",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор публикации",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posts",
                to="blog.category",
                verbose_name="Категория",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posts",
                to="blog.location",
                verbose_name="Местоположение",
            ),
        ),
    ]
