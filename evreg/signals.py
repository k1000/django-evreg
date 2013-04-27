from django.dispatch import Signal

registration_completed = Signal(providing_args=["lang"])
