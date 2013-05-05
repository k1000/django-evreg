# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory

from models import Registry
from settings import *


class RegistrationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['event'].widget = forms.HiddenInput()
        self.event = kwargs["initial"]["event"]
        if self.event.has_daily_prices:
            self.fields["participation"] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label="Event Days",
                initial=[e.id for e in self.event.get_event_days()],
                choices=[[e.id, e.date] for e in self.event.get_event_days()])

    class Meta:
        model = Registry
        exclude = ("created_at", 'status', "payment_id",
                    "payment_amount", "payment_time", "member_validated", "observations")

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        member_type = cleaned_data.get("member_type")
        membership_nr = cleaned_data.get("membership_nr")
        participation = cleaned_data.get("participation")
        gar = cleaned_data.get("gar")

        if self.event.has_daily_prices and not participation:
            raise forms.ValidationError(FORM_ERROR_NO_DAY_SELECTED)
        if int(member_type) > 1 and (not membership_nr or not gar):
            raise forms.ValidationError(FORM_ERROR_MEMEBERSHIP)
        if int(member_type) == 1 and (membership_nr or gar):
            raise forms.ValidationError(FORM_ERROR_MEMEBERSHIP)

        return self.cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        reg = super(RegistrationForm, self).save(commit=False)
        if commit:
            reg.save()
        return reg


class ServiceItemForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ServiceItemForm, self).__init__(*args, **kwargs)
        label = u"%s for %s€, quantity" % (self.initial.get('name', ""),
                                self.initial.get('unit_price', ""))
        self.fields["quantity"].label = label

    id = forms.CharField(widget=forms.HiddenInput())
    unit_price = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.ChoiceField(
        label=_("quantity"),
        choices=enumerate(range(10)),
    )

ServiceOrderFormSet = formset_factory(ServiceItemForm, extra=0)
