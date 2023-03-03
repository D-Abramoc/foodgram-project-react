from django.core import management

from users.models import CustomUser


class Command(management.base.BaseCommand):
    help = 'Upload users'

    def handle(self, *args, **kwargs):
        columns = ('id', 'username', 'email', 'password', 'first_name',
                   'last_name')
        balk_list = []
        for i in range(1, 50):
            id = i + 100
            username = f'user{id}'
            email = f'{username}@fake.fake'
            password = f'pass_{id}_word'
            first_name = f'{username}_First_name'
            last_name = f'{username}_Last_name'
            row = (id, username, email, password, first_name, last_name)
            data_for_model = dict(zip(columns, row))
            balk_list.append(CustomUser(**data_for_model))
        CustomUser.objects.bulk_create(balk_list)
