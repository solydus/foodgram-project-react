import csv
import os

from ingridients.models import Ingredient

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv',
                            nargs='?', type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, options['filename']),
                      'r', encoding='utf-8') as f:
                data = csv.reader(f)
                for row in data:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name, measurement_unit=measurement_unit
                    )
                self.stdout.write(
                    self.style.SUCCESS('Ингредиенты загружены ')
                )
        except FileNotFoundError:
            raise CommandError('Не найден файл ingredients')
