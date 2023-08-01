import json
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

User = get_user_model()


DATA_DIR_PATH = f"{Path(__file__).resolve().parent.parent.parent.parent}/data/"


class Command(BaseCommand):
    ALLOWED_FILE_NAMES = {}

    def handle(self, *args, **options):
        self.upload_all_files(DATA_DIR_PATH)
        return

    def read_file(self, filename):
        with open(filename, encoding="utf-8") as f:
            return json.load(f)

    def upload_all_files(self, full_path):
        for dirpath, dirnames, filenames in os.walk(full_path):
            for filename in filenames:
                data = self.read_file(os.path.join(DATA_DIR_PATH, filename))
                if filename == "ingredients.json":
                    self.upload_ingredients(data)
                elif filename == "tags.json":
                    self.upload_tags(data)
                elif filename == "users.json":
                    self.upload_users(data)
        return

    def upload_tags(self, tags):
        print("--------------------------------------------------------------")
        print("Загружаем теги в базу данных...")
        uploaded = 0
        discarded = 0
        for tag in tags:
            try:
                Tag.objects.create(
                    name=tag["name"].lower(),
                    color=tag["color"].lower(),
                    slug=tag["slug"].lower(),
                )
                uploaded += 1
            except Exception as e:
                print(
                    f"Teг {tag} уже есть в базе данных "
                    f"или не соответствует формату ({e})"
                )
                discarded += 1
        print(
            f"Добавление тегов завершено.\n"
            f"- тегов добавлено: {uploaded}\n"
            f"- тегов отклонено "
            f"(как дубликаты или не соответствующие формату): "
            f"{discarded}"
        )
        return

    def upload_ingredients(self, ingredients):
        print("--------------------------------------------------------------")
        print("Загружаем ингредиенты в базу данных...")
        uploaded = 0
        discarded = 0
        for ingredient in ingredients:
            try:
                Ingredient.objects.create(
                    name=ingredient["name"].lower(),
                    measurement_unit=ingredient["measurement_unit"].lower(),
                )
                uploaded += 1
            except Exception as e:
                print(
                    f"Игредиент {ingredient} уже есть в базе данных "
                    f"или не соответствует формату ({e})"
                )
                discarded += 1
        print(
            f"Добавление ингредиентов завершено.\n"
            f"- ингредиентов добавлено: {uploaded}\n"
            f"- ингредиентов отклонено "
            f"(как дубликаты или не соответствующие формату): "
            f"{discarded}"
        )
        return

    def upload_users(self, users):
        print("--------------------------------------------------------------")
        print("Загружаем пользователей в базу данных...")
        uploaded = 0
        discarded = 0
        for user in users:
            try:
                is_staff = 1 if "is_staff" in user else 0
                is_superuser = 1 if "is_superuser" in user else 0
                User.objects.create(
                    username=user["username"],
                    first_name=user["first_name"].capitalize(),
                    last_name=user["last_name"].capitalize(),
                    email=user["email"],
                    password=user["password"],
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                )

                uploaded += 1
            except Exception as e:
                print(
                    f"Пользователь {user} уже есть в базе данных "
                    f"или не соответствует формату ({e})"
                )
                discarded += 1
        print(
            f"Добавление пользователей завершено.\n"
            f"- пользователей добавлено: {uploaded}\n"
            f"- пользователей отклонено "
            f"(как дубликаты или не соответствующие формату): "
            f"{discarded}"
        )
        return
