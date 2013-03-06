# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from signals import registration_completed


from models import Registry, Event, ParticipationDay
from forms import RegistrationForm, MealOrderFormSet

from shop.cart import Cart


REFISTRY_SUCCESS_MSG = _("""
Thank You for registring for %s. Soon you will recive confirmation email.
""")
EMAIL_MSG = getattr(settings, "EVREG_EMAIL_MSG", dict(
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


def registration(request, event_slug, settings=None):
    event = Event.objects.select_related().get(slug=event_slug)
    registration_form = RegistrationForm(request.POST or None, initial={'event': event})

    if request.method == 'POST':
        if registration_form.is_valid():
            participation_days = registration_form.cleaned_data.get("participation")
            reg = registration_form.save(commit=False)
            reg.payment_amount = reg.calculate_price(participation_days)
            reg.save()

            if reg.event.has_daily_prices:
                for day_id in participation_days:
                    participation_day = ParticipationDay(participant=reg, day_id=int(day_id))
                    participation_day.save()

            # send signal on success
            registration_completed.send(sender=reg, request=request)

            order = Cart(request)
            order.add(reg, reg.payment_amount, 1, reg.__unicode__())
            request.session['reg_id'] = reg.pk
            request.session['client'] = {
                "first_name": reg.first_name,
                "last_name": reg.last_name,
                "email": reg.email,
                "phone": reg.phone,
                "address": reg.address,
                "postal_code": reg.postal_code,
                "state": reg.state,
                "city": reg.city,
                "country": reg.country,
                "member_type": reg.member_type,
            }

            mail_registration_complete(event, reg, request.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse("registration-complete", args=(event.slug,)))

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


def registration_complete(request, slug):
    pk = request.session.get("reg_id")
    registry = Registry.objects.get(pk=pk)
    event = registry.event
    order = Cart(request)
    meal_order_formset = None
    msgs = []

    if event.offers_meals:
        meals = event.meals.all()

        meal_order_formset = MealOrderFormSet(
            request.POST or None,
            initial=[{"id":meal.id, "unit_price":meal.price, "name":meal.description}
                for meal in meals]
        )

        if request.method == "POST":

            if meal_order_formset.is_valid():
                meals_by_id = dict([[meal.id, meal] for meal in meals])
                for form in meal_order_formset:
                    quantity = int(form.cleaned_data['quantity'])

                    if quantity > 0:
                        meal_id = int(form.cleaned_data['id'])
                        meal = meals_by_id[meal_id]
                        order.add(meal, meal.price, quantity, meal.description)

                return HttpResponseRedirect(reverse("checkout"))

    return render(request, "evreg/registration_completed.html",
        {"registry": registry,
        "event": event,
        "meal_order_formset": meal_order_formset,
        "msgs": msgs,
        "order": order
        })
