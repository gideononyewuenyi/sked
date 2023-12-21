from .views import schedule_appointment
from django.urls import path, include

urlpatterns = [
    path('', schedule_appointment, name='schedule-appointment'),
]
