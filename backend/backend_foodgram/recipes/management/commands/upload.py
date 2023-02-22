import csv

from django.core import management

from ...models import Ingredient


class Command(management.base.BaseCommand):
    help = 'Upload data'

    def handle(self, *args, **kwargs):
        path_to_data = (
            '/home/dmitry/Dev/Diploma/'
            'foodgram-project-react/data/ingredients.csv'
        )
        with open(path_to_data, encoding='utf8') as f:
            reader = csv.reader(f)
            heads_of_column = ('name', 'measure')
            # bulk_list = []
            for row in reader:
                data_for_model = dict(zip(heads_of_column, row))
                # bulk_list.append(Ingredient(**data_for_model))
                Ingredient.objects.create(**data_for_model)
