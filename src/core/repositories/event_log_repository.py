from django.db.models import QuerySet

from core.models import EventLogOutbox


class EventLogOutboxRepository:
    @staticmethod
    def filter(kwargs: dict) -> QuerySet:
        """Filter outbox entries based on provided conditions."""
        return EventLogOutbox.objects.filter(**kwargs)

    @staticmethod
    def create(
        event_type: str,
        destination: str,
        event_context: dict,
        **kwargs: dict
    ) -> EventLogOutbox:
        """Create a new outbox entry."""
        return EventLogOutbox.objects.create(
            event_type=event_type,
            destination=destination,
            event_context=event_context,
            **kwargs
        )


event_log_box_repository = EventLogOutboxRepository()
