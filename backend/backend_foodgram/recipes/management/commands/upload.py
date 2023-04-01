import csv

from django.core import management

from ...models import Ingredient


class Command(management.base.BaseCommand):
    help = 'Upload data'

    def handle(self, *args, **kwargs):
        path_to_data = (
            '/app/data/ingredients.csv'
        )
        with open(path_to_data, encoding='utf8') as f:
            reader = csv.reader(f)
            heads_of_column = ('name', 'measure')
            for row in reader:
                data_for_model = dict(zip(heads_of_column, row))
                Ingredient.objects.create(**data_for_model)
