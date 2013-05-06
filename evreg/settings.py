# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

MEMBER_TYPES = getattr(settings, "EVREG_MEMBER_TYPES",
(
    (1, _("Non-member")),
    (2, _("Ordinary")),
    (3, _("Reduced")),
    (4, _("Sustaining")),
    (5, _("Benefactor")),
))

REGISTRY_SUCCESS_MSG = _("""
Thank You for registring for %s. Soon you will recive confirmation email.
""")

EMAIL_MSG = getattr(settings, "EVREG_EMAIL_MSG", dict(
    registration_complete={
        "subject": _("You been registered for %s"),
    },
    inscription_completed={
        "subject": _("You been inscribed for %s"),
    },
    admin_inscription_completed={
        "subject": _("Inscription #%(ref)s for %(event)s completed"),
    },
    admin_delayed_earlibird_payment={
        "subject": _("Delayed earlybird payment #%(ref)s for %(event)s recived"),
    },
    admin_insufficient_payment={
        "subject": _("Insufficient payment #%(ref)s for %(event)s recived"),
    },
))
ADMIN_EMAILS = getattr(settings, "EVREG_ADMIN_EMAILS", [])
FORM_ERROR_MEMEBERSHIP = _("If you are member of Dzogchen Community\
     you must specify your membership number, \
     membership type and Gar you belong.")

FORM_ERROR_MEMEBERSHIP_TYPE = _("Erroneus member type")
FORM_ERROR_NO_DAY_SELECTED = _("You must select at least one day of the event to attend")
