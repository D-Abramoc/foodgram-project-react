import pytest

from users.models import CustomUser
from api.serializers import SpecialUserSerializer


@pytest.mark.django_db
def test_list_users(client):
    response = client.get('/api/users/')
    print(response)
