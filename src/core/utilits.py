from datetime import timedelta
from django.utils.timezone import now


def _one_more_day():
    return now() + timedelta(days=1)
