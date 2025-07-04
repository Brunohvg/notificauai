# Em apps/integrations/urls.py
from django.urls import path
from .views import integrations_view
app_name = 'integrations'

urlpatterns = [
    path('list/', integrations_view, name='integrations'), 
]