from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from core.utilits import _one_more_day


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, # noqa
    ) -> None:
        # https://docs.djangoproject.com/en/5.1/ref/models/fields/#django.db.models.DateField.auto_now
        self.updated_at = timezone.now()

        if isinstance(update_fields, list):
            update_fields.append('updated_at')
        elif isinstance(update_fields, set):
            update_fields.add('updated_at')

        super().save(force_insert, force_update, using, update_fields)


class Status(models.TextChoices):
    FAILED = 'FAILED', 'Failed'
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    SUCCEEDED = 'SUCCEEDED', 'Success'


class EventLogOutbox(TimeStampedModel):
    event_type = models.CharField(max_length=255)
    destination = models.CharField(max_length=100)
    status = models.CharField(default=Status.SCHEDULED, max_length=20, db_index=True,
                              choices=Status.choices)

    event_date_time = models.DateTimeField(default=now)

    event_context = models.JSONField()

    metadata_version = models.PositiveBigIntegerField(default=1)

    expires_at = models.DateTimeField(default=_one_more_day)

    retry = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = 'Logs'

    def __str__(self):
        return f"{self.event_type} - {self.event_date_time}"
