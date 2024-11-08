import logging
from typing import Optional

import celery
from core.celery import app
from core.controllers.event_log_controller import EventLogController

logger = logging.getLogger('django')


class OutBoxEntriesProcessor(celery.Task):
    name = "process_outbox_entries"

    def __init__(self):
        self._event_log_controller = None

    def run(self,
            entries_pk: Optional[int] = None
            ):
        try:

            logger.info(f"Task processing event entries has started")

            self._event_log_controller = EventLogController()
            self._event_log_controller.process_outbox_entries(entries_pk)

        except Exception as err:
            logger.info(f"Task processing event entries has failed with error - {err}")


OutBoxEntriesProcessorTask = app.register_task(
    OutBoxEntriesProcessor()
)
