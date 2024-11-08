import uuid
from collections.abc import Generator
from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings

from core.models import Status
from core.repositories.event_log_repository import event_log_box_repository
from core.schemas.event_log_schema import EventLogOutboxBaseModel
from users.use_cases import CreateUser, CreateUserRequest

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    return CreateUser()


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    f_ch_client.query(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')
    yield


def test_user_created(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    response = f_use_case.execute(request)

    assert response.result.email == 'test@email.com'
    assert response.error == ''


def test_emails_are_unique(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)
    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error == 'User with this email already exists'


def test_event_log_entry_published(
    f_use_case: CreateUser,
    f_ch_client: Client,
) -> None:
    assert not event_log_box_repository.filter(
        {}
    )

    email = f'test_{uuid.uuid4()}@email.com'
    request = CreateUserRequest(
        email=email, first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)

    event_log_obj = event_log_box_repository.filter({}).first()

    assert event_log_obj

    assert event_log_obj.status == Status.SUCCEEDED

    log = f_ch_client.query("SELECT * FROM default.event_log WHERE event_type = 'event_log_outbox_base_model'")

    assert log.result_rows == [
        (
            'event_log_outbox_base_model',
            ANY,
            'Local',
            EventLogOutboxBaseModel.from_orm(event_log_obj).model_dump_json(),
            1,
        ),
    ]
