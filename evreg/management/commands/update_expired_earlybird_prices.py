# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _

from evreg.models import Registry, Event

logger = logging.getLogger("django")


class Command(BaseCommand):
    """
    updates price of not payed in time earlybird registrations
    """
    args = '<event_slug>'
    help = _('''updates price of not payed in time earlybird registrations.
    Requires event_slug argument.
        ''')

    def handle(self, *args, **options):
        event_slug = args[0]
        self.update_earlybird_prices(event_slug)

    def update_earlybird_prices(self, event_slug):
        import ipdb; ipdb.set_trace()
        try:
            event = Event.objects.get(slug=event_slug)
        except Event.DoesNotExist:
            raise CommandError("Event '%s' does not exist" % event_slug)
        earlybird_date = event.earlybird_date
        registrations = Registry.objects.filter(status__exact=1, created_at__lte=earlybird_date)
        for reg in registrations:
            new_price = reg.calculate_price()
            reg.payment_amount = new_price
            reg.save()
