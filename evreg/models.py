# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from international.models import Gar

from django.conf import settings

from signals import inscription_completed, insuficient_payment_received, delayed_earlibird_payment_received
from settings import MEMBER_TYPES
from countries import COUNTRIES_LIST


class Event(models.Model):
    name = models.CharField(_("name"), max_length=250)
    slug = models.SlugField(_("identificator"))
    description = models.TextField(_("description"))
    organizer = models.CharField(_("Organizer"), max_length=250)

    registration_until = models.DateField(_("registration until"),
        null=True, blank=True)
    earlybird_date = models.DateField(_("earlybird date"),
        null=True, blank=True)

    start = models.DateField(_("start"))
    finish = models.DateField(_("finish"))

    venue_name = models.CharField(_("Venue name"), max_length=250)
    venue_address = models.TextField(_("Venue address"))

    contact_email = models.EmailField(_("contact email"))
    contact_tel = models.CharField(_("contact tel"))
    web = models.URLField(_("event web"))

    bank_details = models.TextField(_("bank details"),
        null=True, blank=True)

    success_template_name = models.CharField(_('Success template name'),
        blank=True, null=True,
        max_length=70,
        help_text=_("Example: 'success.html'. If this isn't provided, \
        the system will use 'evreg/payment_form.html'."))

    @property
    def title(self):
        return u"%(name)s, %(start)s - %(finish)s, %(venue_name)s" % {
            "name": self.name,
            "start": str(self.start),
            "finish": str(self.finish),
            "venue_name": self.venue_name
        }

    @property
    def is_earlybird(self):
        if self.earlybird_date:
            return (datetime.date.today() < self.earlybird_date)
        return None

    @property
    def offers_meals(self):
        return self.get_meals()

    def get_meals(self):
        """
        Memoizing event days
        """
        self._event_meals = getattr(self, "_event_meals", self.meals.all())
        return self._event_meals

    @property
    def is_finished(self):
        return (datetime.date.today() > self.finish)

    @property
    def is_registration_active(self):
        registration_until = self.registration_until or self.finish
        return (datetime.date.today() < registration_until)

    @property
    def has_daily_prices(self):
        return (self.get_daily_prices())

    def get_member_prices(self):
        """
        Memoizing member prices
        """
        self._member_prices = getattr(self, "_member_prices", self.member_prices.all())
        return self._member_prices

    def get_event_days(self):
        """
        Memoizing event days
        """
        self._event_days = getattr(self, "_event_days", self.days.all())
        return self._event_days

    def get_daily_prices(self):
        """
        Memoizing daily prices
        """
        self._daily_prices = getattr(self,
                "_daily_prices",
                MemberPricesPerDay.objects.select_related().filter(day__event=self.pk).order_by("id")
        )
        return self._daily_prices

    def list_member_pices(self):
        """
        returns current whole event prices per member. Earlybird applied
        """
        def establish_early(obj):
            if self.is_earlybird:
                return obj.earlybird_price
            else:
                return obj.price

        return [[smart_str(m_price.get_member_type_display()),
            establish_early(m_price)] for m_price in self.get_member_prices()]

    def list_per_day_prices(self, group_on="member_type"):
        """
        returns current per day prices. Earlybird applied
        """

        objects = {}
        per_day_prices = self.get_daily_prices()
        for day_prices in per_day_prices:
            atr = str(getattr(day_prices, group_on))
            if self.is_earlybird and day_prices.earlybird_price:
                current_price = day_prices.earlybird_price
            else:
                current_price = day_prices.price
            if atr in objects:
                objects[atr].append(current_price)
            else:
                objects[atr] = [current_price]

        return objects or 0

    def __unicode__(self):
        return self.name


class MemberPrices(models.Model):
    event = models.ForeignKey(Event,
        related_name='member_prices',
        verbose_name=_("Event"))
    member_type = models.PositiveSmallIntegerField(_("Member type"),
            choices=MEMBER_TYPES
    )
    price = models.IntegerField(_("full price"))
    earlybird_price = models.IntegerField(_("earlybird price"),
        null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = _('Member Prices')


class EventDay(models.Model):
    """docstring for Day"""
    event = models.ForeignKey(Event,
        related_name="days",
        verbose_name=_("Event"))
    date = models.DateField(_("date"),
        null=True, blank=True)
    programme = models.TextField(_("programme"),
        null=True, blank=True)

    class Meta:
        verbose_name = _('event day')
        verbose_name_plural = _('event days')

    def __unicode__(self):
        return u"%s %s" % (self.event, unicode(self.date))


class Meal(models.Model):
    """
    Event meals
    """
    event = models.ForeignKey(Event,
        related_name='meals',
        verbose_name=_("Event"))
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(_("description"))
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Service')

    def __unicode__(self):
        return self.description


class MemberPricesPerDay(models.Model):
    day = models.ForeignKey(EventDay,
        related_name="per_day_prices",
        verbose_name=_("Day"))
    member_type = models.PositiveSmallIntegerField(_("Member type"),
            choices=MEMBER_TYPES
    )
    price = models.IntegerField(_("full price"))
    earlybird_price = models.IntegerField(_("earlybird price"),
        null=True, blank=True)


class Registry(models.Model):
    """Registry model"""

    STATUS = (
        (1, _("not payed")),
        (2, _("payed")),
        (3, _("canceled")),
    )

    event = models.ForeignKey(Event, verbose_name=_("Event"))

    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)

    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)

    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20,
        blank=True, null=True,)

    address = models.TextField(_("address"), max_length=250)
    postal_code = models.CharField(_("zip"), max_length=8,
        blank=True, null=True,)
    state = models.CharField(_("State/Region"), max_length=100)
    city = models.CharField(_("city"), max_length=100)

    country = models.CharField(_("country"),
        max_length=50,
        # choices=sorted(codes.items(), key=itemgetter(1)),
        choices=COUNTRIES_LIST,
        default=str(settings.LANGUAGE_CODE.upper()),
    )

    member_type = models.PositiveSmallIntegerField(
            _("member of Dzogchen Community"),
            default=1,
            choices=MEMBER_TYPES,
    )
    membership_nr = models.PositiveSmallIntegerField(
            _("membership nr"),
            max_length=5,
            blank=True, null=True,
    )
    gar = models.ForeignKey(Gar,
        verbose_name=_("gar"),
        blank=True, null=True,
        help_text=_("Leave it empty if you dont know")
    )

    member_validated = models.BooleanField(
        _("is valid member?"),
        default=False,
    )
    # karmayoga = models.TextField(_("karmayoga"),
    #     blank=True, null=True,
    #     help_text=_("Do you want to help?")
    # )

    observations = models.TextField(_("observations"),
        blank=True, null=True,
    )
    newsletter = models.BooleanField(_("Receive Newsletter"))
    comments = models.TextField(_("comments, How did you find out about us?"),
        blank=True, null=True,
    )

    payment_time = models.DateTimeField(_("payment time"),
        blank=True, null=True,
    )
    payment_amount = models.PositiveSmallIntegerField(_("amount to pay "),
        blank=True, null=True,
    )
    payment_id = models.PositiveIntegerField(_("payment id"),
        blank=True, null=True,
    )

    status = models.PositiveSmallIntegerField(
            _("status"),
            choices=STATUS,
            default=1,
    )

    @property
    def participation_days(self):
        return [day[0] for day in self.participationday_set.values_list("day__date")]

    @property
    def event_days(self):
        return self.event.days.all()

    def get_member_prices(self, member_type):
        return self.event.member_prices.get(member_type=member_type)

    def calculate_price(self, participation_days):
        """
        participation_days = [u'1', u'2']
        """
        event_days = self.event_days
        # whole event
        if not self.event.has_daily_prices or len(event_days) == len(participation_days):
            member_type_price = self.get_member_prices(member_type=self.member_type)
            if self.event.earlybird_date and self.event.is_earlybird:
                price = member_type_price.earlybird_price
            else:
                price = member_type_price.price
        else:
            price = 0
            event_days_participation = [event_day for event_day in event_days if unicode(event_day.pk) in participation_days]
            for day in event_days_participation:
                day_prices = day.per_day_prices.get(member_type=self.member_type)
                if self.event.earlybird_date and self.event.is_earlybird and day_prices.earlybird_price:
                    price = price + day_prices.earlybird_price
                else:
                    price = price + day_prices.price

        return price

    def make_payment(self, payment_id, amount=None):
        import datetime
        self.payment_time = datetime.datetime.now()
        self.status = 2
        self.payment_id = payment_id

        self.save()

        # send signal
        inscription_completed.send(sender=self)

        # TODO check if it is eanought mone etc

        # participation_days_ids = [unicode(day.id) for day in self.participationday_set.all()]
        # import ipdb; ipdb.set_trace()
        # actual_price = self.calculate_price(participation_days_ids)

        # if actual_price >= self.payment_amount:
        #     self.payment_time = datetime.datetime.now()
        #     self.status = 2
        #     self.payment_id = payment_id

        #     self.save()

        #     # send signal
        #     inscription_completed.send(sender=self)
        # elif self.event.is_earlybird:
        #     # diference must be payed
        #     diference_to_pay = actual_price - self.payment_amount
        #     # send signal notify administrator and client
        #     delayed_earlibird_payment_received.send(
        #         sender=self,
        #         payment_id=payment_id,
        #         diference_to_pay=diference_to_pay,)
        # else:
        #     # payed too less
        #     insuficient_payment_received.send(
        #         sender=self,
        #         payment_id=payment_id,
        #         amount=amount,)

    class Meta:
        verbose_name = _('Registry')
        verbose_name_plural = _('Registry')

    def __unicode__(self):
        participation_days = [str(day.day) for day in self.participation_days]
        return _(u"R-%(id)s %(first_name)s %(last_name)s (%(member_type)s) %(event)s at days %(days)s") % {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "member_type": MEMBER_TYPES[self.member_type - 1][1],  # ???? self.get_member_type_display,
            "event": self.event.__unicode__(),
            "days": ", ".join(participation_days)
        }


class ParticipationDay(models.Model):
    participant = models.ForeignKey(Registry, verbose_name=_("Registry"))
    day = models.ForeignKey(EventDay,
        related_name="participation_days",
        verbose_name=_("Day"))
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
