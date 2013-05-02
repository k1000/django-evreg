# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.translation import get_language

from signals import registration_completed

from models import Registry, Event, ParticipationDay
from forms import RegistrationForm, ServiceOrderFormSet

from shop.cart import Cart, OrderAlreadyCheckedout


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

            request.session['reg_id'] = reg.pk

            if not request.session.get('client', None):
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

            # send signal on success
            registration_completed.send(sender=reg, lang=get_language(), request=request)

            return redirect("registration-complete", event.slug)

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

        meal_order_formset = ServiceOrderFormSet(
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
                        try:
                            order.add(meal, meal.price, quantity, meal.description)
                        except OrderAlreadyCheckedout:
                            return redirect("payment", order.cart.id)

                return redirect("checkout")

    return render(request, "evreg/registration_completed.html",
        {"registry": registry,
        "event": event,
        "meal_order_formset": meal_order_formset,
        "msgs": msgs,
        "order": order
        })

from notify import *
