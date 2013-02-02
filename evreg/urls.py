from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('evreg.views',
    url(r'^payment/(?P<slug>.*)/$', "payment", name='payment-form'),
    url(r'^payment/sucess/', "payment_sucess", name='payment-sucess'),
    url(r'^payment/failure/', "payment_failure", name='payment-failure'),
    url(r'^(?P<slug>.*)/$', "render_registartion", name='registration-form'),
)
