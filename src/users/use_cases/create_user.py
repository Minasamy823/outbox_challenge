from typing import Any

import structlog
from django.db import transaction
from core.base_model import Model
from core.models import EventLogOutbox
from core.repositories.event_log_repository import event_log_box_repository
from core.tasks.outbox_entries_processor_task import OutBoxEntriesProcessorTask
from core.use_case import UseCase, UseCaseRequest, UseCaseResponse
from users.models import User

logger = structlog.get_logger(__name__)


class UserCreated(Model):
    email: str
    first_name: str
    last_name: str


class CreateUserRequest(UseCaseRequest):
    email: str
    first_name: str = ''
    last_name: str = ''


class CreateUserResponse(UseCaseResponse):
    result: User | None = None
    error: str = ''


class CreateUser(UseCase):
    def _get_context_vars(self, request: UseCaseRequest) -> dict[str, Any]:
        return {
            'email': request.email,
            'first_name': request.first_name,
            'last_name': request.last_name,
        }

    @transaction.atomic()
    def _execute(self, request: CreateUserRequest) -> CreateUserResponse:
        try:
            logger.info('Creating a new user')

            user, created = User.objects.get_or_create(
                email=request.email,
                defaults={
                    'first_name': request.first_name, 'last_name': request.last_name,
                },
            )

            if created:
                logger.info('User has been created')
                event_log_obj = self._log(user)

                OutBoxEntriesProcessorTask.delay(
                    [event_log_obj.pk]
                )

                return CreateUserResponse(result=user)

            logger.error('Unable to create a new user')
            return CreateUserResponse(error='User with this email already exists')

        except Exception as err:
            logger.error(f'Received error while creating a user -> {err}')

    def _log(self, user: User) -> EventLogOutbox:
        logger.info('Creating log in event_log_box_repository')

        log_obj: EventLogOutbox = event_log_box_repository.create(
            event_type='creating user',
            destination='clickhouse',
            event_context=UserCreated(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ).dict()
        )

        return log_obj

        logger.info('Successfully created log in event_log_box_repository')
