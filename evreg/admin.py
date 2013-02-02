 # -*- coding: utf-8 -*-
from django.contrib import admin

from models import Registry, Event, MemberPrices, EventDay, MemberPricesPerDay, ParticipationDay


class ParticipationDayInline(admin.TabularInline):
    model = ParticipationDay


class RegistryAdmin(admin.ModelAdmin):
    inlines = [
        ParticipationDayInline
    ]

    fieldsets = (
        (None, {
            'fields': (
                'event',
                ('first_name', 'last_name'),
                'status',
                ('email', 'phone',),
                'address',
                ('postal_code', "city",),
                'country',
                ('member_type', 'membership_nr', 'gar'),
                'karmayoga',
                ('payment_time', 'payment_amount', 'payment_id')),
        }),
    )
    list_display = ('first_name', 'last_name', 'event', 'status', 'member_type')
    list_filter = ['event', 'gar', 'status', 'member_type', 'karmayoga']
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


class EventAdmin(admin.ModelAdmin):
    inlines = [
        MemberPricesInline, EventDayInline
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'slug'),
                ('start', 'finish'),
                'description',
                'organizer',
                ('contact_email', 'web'),
                ('venue_name', 'venue_address'),
                ('registration_until', 'earlybird_date',),
                'bank_details'
        )}),
    )
    list_display = ('name', 'start')
    prepopulated_fields = {"slug": ("name",)}


class EventDayAdmin(admin.ModelAdmin):
    inlines = [
        MemberPricesPerDayInline,
    ]
    list_display = ('event', 'date')
    list_filter = ['event']
    extra = 1

admin.site.register(EventDay, EventDayAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registry, RegistryAdmin)
