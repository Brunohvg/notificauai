# Em apps/integrations/urls.py
from django.urls import path
from .views import integrations_view, integrations_delete
app_name = 'integrations_ui'

urlpatterns = [
    path('list/', integrations_view, name='integrations'), 
    path('delete/<int:integration_id>/', integrations_delete, name='integrations_delete'),
]