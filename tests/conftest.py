from django.conf import settings
from django.core.management import call_command
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def pytest_configure():
    # settings.configure(DATABASES=...)
    settings.DATABASES["default"]["NAME"] = BASE_DIR / "test_db.sqlite3"


@pytest.fixture(scope="module")
def django_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("sqlflush")
        call_command("migrate")
        # call_command("migrate", "--noinput")
        # Putting the yield here means that you keep the unblocked context
        # while your ptest test runs, which is surely what you want
        yield None
