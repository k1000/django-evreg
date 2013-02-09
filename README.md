Django evreg - event registration
=================================

Event registration
Tested with django 1.4.3

Features:
* Unlimited events
* Multilanguage support
* Event info includes: name, dates, description, venue, contact email, etc.
* Prices for whole event & early bird prices
* Individual prices for separate days
* Prices calculated according to membership type
* Confirmation email for the client
* Support of online payemnt ex: PayPal

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
* EVREG_PAYMENT_TEMPLATE = "evreg/payment_form.html"
* EVREG_EMAIL_MSG 

Thanx
-----
Thanks to German Dzogchen Community Gakyil for letting share this work.


Licence
-------
