import logging
from typing import Optional
from django.db.models import QuerySet
from core.event_log_client import EventLogClient
from core.models import Status, EventLogOutbox
from core.repositories.event_log_repository import event_log_box_repository
from core.schemas.event_log_schema import EventLogOutboxBaseModel

logger = logging.getLogger(__name__)


class EventLogController:

    def process_outbox_entries(self, entries_pk: Optional[int] = None):
        entries = self._get_unproccessed_entries(entries_pk)

        for entry in entries:
            try:

                event_log_schema = self._build_obj_from_orm(entry)

                with EventLogClient.init() as client:
                    client.insert(
                        data=[event_log_schema]
                    )
                entry.status = Status.SUCCEEDED
                entry.save()

            except Exception as e:
                logger.error(f"Failed to process outbox entry {entry.id}: {e}")
                continue

    def _build_obj_from_orm(self, entry: EventLogOutbox) -> EventLogOutboxBaseModel:
        return EventLogOutboxBaseModel.from_orm(entry)

    def _get_unproccessed_entries(self,
                                  entries_pk: Optional[int] = None
                                  ) -> QuerySet:

        filters = {
            "status": Status.SCHEDULED
        }

        if entries_pk:
            filters["pk__in"] = entries_pk

            return event_log_box_repository.filter(
                filters
            ).order_by('created_at')
