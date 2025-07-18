from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('apps.accounts.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls_api', namespace='integrations_api')),
    path('integracoes/', include('apps.integrations.urls_ui', namespace='integrations_ui' )),
    path('pedidos/', include('apps.orders.urls_ui', namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
