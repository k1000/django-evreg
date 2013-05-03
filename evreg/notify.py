# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from signals import registration_completed, inscription_completed


REFISTRY_SUCCESS_MSG = _("""
Thank You for registring for %s. Soon you will recive confirmation email.
""")
EMAIL_MSG = getattr(settings, "EVREG_EMAIL_MSG", dict(
    registry_succes={
        "subject": _("You been registered for %s"),
    },
))


def mail_registration_complete(event, reg, lang):
    email_var = {"event": event, "person": reg}
    email_template_name = "evreg/registration_confirmation-%s.mail" % lang
    send_mail(
                EMAIL_MSG['registry_succes']['subject'] % event.title,
                get_template(email_template_name).render(Context(email_var)),
                event.contact_email,
                [reg.email],
                fail_silently=True
            )


def notify_registration_complete(**kwargs):
    reg = kwargs["sender"]
    mail_registration_complete(reg.event, reg, kwargs["lang"])


registration_completed.connect(notify_registration_complete)


def mail_inscription_completed(reg, lang):
    email_var = {"event": reg.event, "person": reg}
    email_template_name = "evreg/registration_confirmation-%s.mail" % lang
    send_mail(
                EMAIL_MSG['registry_succes']['subject'] % reg.event.title,
                get_template(email_template_name).render(Context(email_var)),
                reg.event.contact_email,
                [reg.email],
                fail_silently=True
            )


def notify_inscription_completed(**kwargs):
    reg = kwargs["sender"]
    lang = kwargs["lang"]
    mail_inscription_completed(reg, lang)

inscription_completed.connect(notify_registration_complete)
