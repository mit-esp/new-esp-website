"""
Common model factories
"""
from factory import Faker
from factory.django import DjangoModelFactory

from common.models import User


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    username = Faker("username")

    class Meta:
        model = User
