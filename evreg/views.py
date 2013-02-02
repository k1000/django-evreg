# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

from forms import RegistrationForm
from models import Registry, Event, ParticipationDay

from django.conf import settings

PAYMENT_TEMPLATE = getattr(settings, "PAYMENT_TEMPLATE", "evreg/payment_form.html")
PAYMENT_URL = getattr(settings, "PAYMENT_URL", reverse("payment-form"))
EMAIL_MSG = getattr(settings, "EMAIL_MSG", dict(
    registry_succes={
        "subject": _("You been registered for %s"),
    },
    payment_sucess={
        "subject": _("We recived payment for %s"),
        "message": _("""
    Thank You.
    You been registered for %<name>s
    """)
    },
    payment_failure={
        "subject": _("There been error in payment for %s"),
        "message": _("""
    Sorry.
    There been error in processing your payment.
    Please contact us:

    Thank you
    """)
    },
))


def registration(request, event_slug, settings=None):
    event = Event.objects.select_related().get(slug=event_slug)
    registration_form = RegistrationForm(request.POST or None, initial={'event': event})

    if request.method == 'POST':
        if registration_form.is_valid():
            participation_days = registration_form.cleaned_data.get("participation")
            reg = registration_form.save(commit=False)
            reg.payment_amount = reg.calculate_price(participation_days)
            reg.save()

            for day_id in participation_days:
                participation_day = ParticipationDay(participant=reg, day_id=int(day_id))
                participation_day.save()

            request.session['to_pay'] = reg.payment_amount
            request.session['reg_id'] = reg.pk
            email_var = {"event": event, "person": reg}

            email_template_name = "evreg/retreat_registration_confirmation-%s.mail" % request.LANGUAGE_CODE
            send_mail(
                EMAIL_MSG['registry_succes']['subject'] % event.title,
                get_template(email_template_name).render(Context(email_var)),
                event.contact_email,
                [reg.email],
                fail_silently=True
            )

            return HttpResponseRedirect(reverse("payment-form", args=(event.slug,)))

    return {"registration_form": registration_form,
            "event": event,
            "event_days": event.get_event_days(),
            "list_member_pices": event.list_member_pices(),
            "member_prices": event.get_member_prices()}


def render_registartion(request, slug):
    reg = registration(request, slug)
    if type(reg) is dict:
        return render(request,
            "evreg/registration_form.html",
            reg
        )
    else:
        return reg


def payment(request, slug):
    pk = request.session.get("reg_id")
    registry = Registry.objects.get(pk=pk)
    event = registry.event

    return render(request, PAYMENT_TEMPLATE,
        {"registry": registry, "event": event})


def payment_sucess(request):
    return render(request, PAYMENT_TEMPLATE, {})


def payment_failure(request):
    return render(request, PAYMENT_TEMPLATE, {})
