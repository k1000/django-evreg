Django evreg - event registration
=================================

Event registration

Features:
* Unlimited events
* Multilanguage support
* Event info includes: name, dates, description, venue, contact email, venue etc.
* Whole event & early bird prices
* Individual prices for separate days
* Prices calculated according to membership
* Confirmation email for the client
* Pay online via PayPal

Installing
----------
Assuming that you got virtualenv installed activated.

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

Thanx
-----
Thanks to German Dzogchen Community Gakyil for letting share this work.


Licence
-------
