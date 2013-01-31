Django evreg - event registration
=================================

Event registration
Simple, extendible CMS writen on the top of Django. 

Features:
* Unlimited events
* Basic event info including: name, dates, description, venue, contact email
* Early bird prices
* Whole event prices
* Program with prices for separate days
* Prices calculated according to membership
* Confirmation email to client
* Pay online via PayPal

Installing
----------
Install via pip:

    pip install -e git+https://github.com/k1000/django-evreg.git#egg=evreg

Add to INSTALLED_APPS in settings.py:
    
    'evreg',

Add to 'urlpatterns' (at the end) urls.py:
    
    (r'', include('evreg.urls')),
    
Create tables etc.:

    python manage.py syncdb

Config
------

Thanx
-----
Thanks to German Dzogchen Community Gakyil for letting share this work.


Licence
-------
