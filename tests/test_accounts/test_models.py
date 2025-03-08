from accounts.models import User
import pytest


@pytest.mark.django_db
def test_create_user(django_db):
    user = User.objects.create_user(
        email="test@test.test",
        username="test",
        bio="myBIO",
    )
    assert user.email == "test@test.test"
    assert user.username == "test"
    assert user.bio == "myBIO"
