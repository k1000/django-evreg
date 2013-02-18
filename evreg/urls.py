from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('evreg.views',
    url(r'^complete/(?P<slug>.*)/$', "registration_complete", name='registration-complete'),
    url(r'^(?P<slug>.*)/$', "render_registartion", name='registration-form'),
)
