 # -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django_exportable_admin.admin import CSVExportableAdmin
from models import Registry, Event, MemberPrices, EventDay, MemberPricesPerDay, ParticipationDay, Meal


class ParticipationDayInline(admin.TabularInline):
    model = ParticipationDay


class RegistryAdmin(CSVExportableAdmin):
    inlines = [
        ParticipationDayInline
    ]

    fieldsets = (
        (None, {
            'fields': (
                'event',
                ('first_name', 'last_name'),
                'status',
                'observations')
        }),
        (_('Contact'),
            {
            'fields': (
                ('email', 'phone',),
                'address',
                ('postal_code', "city",),
                'country',
                ),
        }),
        (_('Membership'),
            {
            'fields': (('member_type', 'member_validated',)
                        ('gar', 'membership_nr'),
                )}
        ),
        (_('Payment'),
            {
            'fields': (('payment_time', 'payment_amount', 'payment_id'),
                )}
        ),
    )
    list_display = ['first_name', 'last_name', 'id', 'event', 'status', 'member_type', 'member_validated']
    csv_list_display = list_display + ["membership_nr", "gar", "email", "payment_amount"]
    list_filter = ['event', 'gar', 'status', 'member_type', ]
    search_fields = ['last_name', 'email', 'membership_nr']


class MemberPricesInline(admin.TabularInline):
    model = MemberPrices
    extra = 0


class MemberPricesPerDayInline(admin.TabularInline):
    model = MemberPricesPerDay
    extra = 0


class EventDayInline(admin.TabularInline):
    model = EventDay
    inlines = [
        MemberPricesPerDayInline
    ]
    extra = 0


class MealInline(admin.TabularInline):
    model = Meal
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [
        MemberPricesInline, EventDayInline, MealInline
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug'),
                ('start', 'finish'),
                'description',
                ('organizer', 'contact_tel'),
                ('contact_email', 'web'),
                ('venue_name', 'venue_address'),
                ('registration_until', 'earlybird_date',),
                'bank_details',
        )}),
        (_('Advanced options'),
            {'classes': ('collapse',),
            'fields': ('success_template_name',)}
        ),
    )
    list_display = ('name', 'start')
    prepopulated_fields = {"slug": ("name",)}


class EventDayAdmin(admin.ModelAdmin):
    inlines = [
        MemberPricesPerDayInline,
    ]
    list_filter = ['event']
    extra = 1

admin.site.register(EventDay, EventDayAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registry, RegistryAdmin)
