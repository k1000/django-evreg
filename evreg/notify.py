# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site

from signals import registration_completed
from signals import inscription_completed
from signals import delayed_earlibird_payment_received
from signals import insuficient_payment_received

from settings import *

SITE = Site.objects.get_current()


def mail_registration_complete(event, reg, lang):
    email_var = {"event": event, "person": reg}
    email_template_name = "evreg/registration_confirmation-%s.mail" % lang
    send_mail(
                EMAIL_MSG['registration_complete']['subject'] % event.title,
                get_template(email_template_name).render(Context(email_var)),
                event.contact_email,
                [reg.email],
                fail_silently=True
            )


def notify_registration_complete(**kwargs):
    reg = kwargs["sender"]
    mail_registration_complete(reg.event, reg, kwargs["lang"])


def mail_inscription_completed(reg, lang):
    email_var = {"event": reg.event, "person": reg}
    email_template_name = "evreg/inscription_completed-%s.mail" % lang
    send_mail(
                EMAIL_MSG['inscription_completed']['subject'] % reg.event.title,
                get_template(email_template_name).render(Context(email_var)),
                reg.event.contact_email,
                [reg.email],
                fail_silently=True
            )


def notify_inscription_completed(**kwargs):
    mail_inscription_completed(kwargs["sender"], kwargs["lang"])


def mail_admin_inscription_completed(reg, **kwargs):
    email_var = {"event": reg.event, "person": reg}
    email_template_name = "evreg/admin-inscription_completed.mail"
    send_mail(
                EMAIL_MSG['admin_inscription_completed']['subject'] % (reg.id, reg.event.name),
                get_template(email_template_name).render(Context(email_var)),
                reg.event.contact_email,
                [reg.event.contact_email],
                fail_silently=True
            )


def mail_admin_delayed_earlibird_payment(reg, **kwargs):
    from datetime import date
    delay = reg.event.earlybird_date - date.today()
    email_var = {"event": reg.event,
            "person": reg,
            "delay": delay,
            "payment_id": kwargs["payment_id"],
            "diference_to_pay": kwargs["diference_to_pay"]}
    email_template_name = "evreg/admin-delayed_earlibird_payment.mail"
    send_mail(
                EMAIL_MSG['admin_delayed_earlibird_payment']['subject'] % (reg.id, reg.event.name),
                get_template(email_template_name).render(Context(email_var)),
                reg.event.contact_email,
                [reg.event.contact_email],
                fail_silently=True
            )


registration_completed.connect(notify_registration_complete)
inscription_completed.connect(notify_inscription_completed)
inscription_completed.connect(mail_admin_inscription_completed)
delayed_earlibird_payment_received.connect(mail_admin_delayed_earlibird_payment)
# TODO insuficient payment
