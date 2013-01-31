from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', "registration.views.render_registartion", name='registration-form'),
    url(r'^payment/$', "registration.views.payment", name='payment-form'),
    url(r'^payment/sucess/', "registration.views.payment_sucess", name='payment-sucess'),
    url(r'^payment/failure/', "registration.views.payment_failure", name='payment-failure'),
)
