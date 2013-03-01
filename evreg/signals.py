import django.dispatch

registration_completed = django.dispatch.Signal(providing_args=["request"])
