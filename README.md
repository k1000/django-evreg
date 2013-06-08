Django evreg - event registration
=================================

Event registration
Tested with django 1.4.3

Features:
* Unlimited events
* Multilanguage support
* Event info includes: name, dates, description, venue, contact email, etc.
* Prices for whole event & optional early bird prices 
* Individual prices for separate days
* Prices calculated according to membership type
* Notificatios via email to the client
* Reservation of arbitrary aditional services as meal, cD etc.
* Easy integration with online payemnts gateways ex: PayPal

Installing
----------
Assuming that you got virtualenv (python virtual envirement) created and activated.

Install via pip:

    pip install -e git+https://github.com/k1000/django-evreg.git#egg=evreg

Add to "INSTALLED_APPS" in settings.py file:
    
    'evreg',

Add to 'urlpatterns' (at the end) urls.py file:
    
    (r'registration', include('evreg.urls')),
    
Create tables etc.:

    python manage.py syncdb

Config
------
Optionally you may set in settings.py file:

* EVREG_MEMBER_TYPES = ((1, _("Non-member")), (2, _("Member")))
* EVREG_EMAIL_MSG 
* EVREG_ADMIN_EMAILS

Thanx
-----
Thanks to German Dzogchen Community Gakyil for letting share this work.


Licence
-------
