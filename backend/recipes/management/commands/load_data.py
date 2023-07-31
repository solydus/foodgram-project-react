import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.import_ingridients()
        self.import_tags()
        self.stdout.write(
            self.style.SUCCESS('All import success')
        )

    def import_ingridients(self):
        text = 'Ингридиенты успешно загружены'
        with open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r',
            encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        self.stdout.write(
            self.style.NOTICE(text)
        )

    def import_tags(self):
        text = 'Тэги успешно загружены'
        with open(
            f'{settings.BASE_DIR}/data/tags.csv',
            'r',
            encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                Tag.objects.get_or_create(
                    name=row[0],
                    slug=row[1],
                    color=row[2]
                )
        self.stdout.write(
            self.style.NOTICE(text)
        )
