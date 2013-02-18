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

from shop.cart import Cart
from shop.forms import ItemForm

from django.conf import settings

PAYMENT_TEMPLATE = getattr(settings, "EVREG_PAYMENT_TEMPLATE", "evreg/payment_form.html")

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

            # request.session['to_pay'] = reg.payment_amount
            order = Cart(request)
            order.add(reg, reg.payment_amount, 1)
            request.session['reg_id'] = reg.pk

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
    meal_order_form = None
    msgs = []

    if event.offers_meals:
        meal = event.meals.all()[0]  # TODO support multiple meals offers per event
        meal_order_form = ItemForm(
            request.POST or None,
            initial={"unit_price": meal.price},
            item_label=_("meals number"),
            items_nr=len(registry.participation_days) + 1
        )
        if request.method == "POST":
            nr_meals = meal_order_form.data.get('nr_items')
            order.add(meal, meal.price, nr_meals)
            msgs.append(_("%s meal has been added" % nr_meals))

        # OrderMealsFormSet = make_order_items_form(
        #     extra=3,
        #     fields=['quantity', 'unit_price']
        # )
        # order_meals_formset = OrderMealsFormSet(
        #     request.POST or None,
        #     queryset=Meal.objects.filter(meal__event=event),
        # )

        # if order_meals_formset.is_valid():
        #     for form in order_meals_formset:
        #         if form.cleaned_data.get('is_checked'):
        #             form.save()
        #             order = Cart(request)
        #             meal = form.instance
        #             order.add(meal, meal.payment_amount, 1)

    return render(request, PAYMENT_TEMPLATE,
        {"registry": registry,
        "event": event,
        "meal_order_form": meal_order_form,
        "msgs": msgs,
        "order": order
        })


def payment_sucess(request):
    return render(request, PAYMENT_TEMPLATE, {})


def payment_failure(request):
    return render(request, PAYMENT_TEMPLATE, {})
