from django.urls import path
from .views import logs_view

urlpatterns = [
    path('logs', logs_view, name='logs'),
]
